from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import os
import csv
import zipfile
import uuid
import tempfile
import requests
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings
from app.features.products import models, schemas
from app.features.products.models import Product


async def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """
    Get all products with pagination.
    
    Args:   
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of products
    """
    return db.query(models.Product).offset(skip).limit(limit).all()


async def get_product(db: Session, product_id: int) -> models.Product:
    """
    Get a product by ID.
    
    Args:
        db: Database session
        product_id: ID of the product to retrieve
        
    Returns:
        Product if found
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


async def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """
    Create a new product.
    
    Args:
        db: Database session
        product: Product data
        
    Returns:
        Created product
    """
    db_product = models.Product(
        sku=product.sku,
        name=product.name,
        description=product.description,
        keywords=product.keywords,
        category=product.category,
        images=product.images,
        audio_description=product.audio_description,
        audio=product.audio,
        audio_config=product.audio_config,
        additional_context=product.additional_context,
        image_description=product.image_description,
        vendor_url=product.vendor_url,
        vendor_context=product.vendor_context,
        selected_context_source=product.selected_context_source,
        uploaded_image=product.uploaded_image
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


async def update_product(
    db: Session, 
    product_id: int, 
    product_update: schemas.ProductUpdate
) -> models.Product:
    """
    Update a product.
    
    Args:
        db: Database session
        product_id: ID of the product to update
        product_update: Updated product data
        
    Returns:
        Updated product
        
    Raises:
        HTTPException: If product not found
    """
    db_product = await get_product(db, product_id)
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


async def delete_product(db: Session, product_id: int) -> models.Product:
    """
    Delete a product.
    
    Args:
        db: Database session
        product_id: ID of the product to delete
        
    Returns:
        Deleted product
        
    Raises:
        HTTPException: If product not found
    """
    db_product = await get_product(db, product_id)
    
    db.delete(db_product)
    db.commit()
    return db_product




async def create_export_zip(db: Session, product_id: Optional[int] = None) -> dict:
    """
    Creates a ZIP file containing product data: images, audio files, and CSV.
    If product_id is provided, exports only that product.
    If product_id is not provided, exports all products.
    
    Args:
        db: Database session
        product_id: Optional ID of the product to export
        
    Returns:
        Dictionary with export information
    """
    # Create export directory if it doesn't exist
    export_dir = settings.EXPORTS_DIR
    export_dir.mkdir(exist_ok=True)
    
    # Generate unique filename for the export
    timestamp = uuid.uuid4().hex[:8]
    
    if product_id:
        # Get specific product from database
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        products = [product]
        export_filename = f"product_{product_id}_export_{timestamp}.zip"
    else:
        # Get all products from database
        products = db.query(Product).all()
        if not products:
            raise HTTPException(status_code=404, detail="No products found in database")
        export_filename = f"all_products_export_{timestamp}.zip"
    
    export_path = export_dir / export_filename
    products_count = len(products)
    images_count = 0
    audio_count = 0
    
    with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Single product vs all products
        if product_id:
            # Single product export
            product = products[0]
            # Create folder name using product SKU and name
            clean_name = "".join(c for c in product.name if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_name = clean_name.replace(' ', '_')
            folder_name = f"{product.sku}_{clean_name}"
            
            # Create CSV with product data
            csv_content = _create_product_csv(product)
            zipf.writestr(f"{folder_name}/product.csv", csv_content)
            
            # Track temp files to clean up later
            temp_files = []
            
            # Process images
            if product.images:
                for i, image_url in enumerate(product.images):
                    try:
                        image_path, is_temp = _get_local_file_path(image_url, "images")
                        if image_path and image_path.exists():
                            # Add images to product folder/images - using SKU in filename
                            zip_path = f"{folder_name}/images/{product.sku}_{i+1}{image_path.suffix}"
                            zipf.write(image_path, zip_path)
                            images_count += 1
                            
                            # Track temp file for cleanup
                            if is_temp:
                                temp_files.append(image_path)
                    except Exception as e:
                        print(f"Warning: Could not add image {image_url} for product {product.id}: {e}")
            
            # Process audio
            if product.audio:
                try:
                    audio_path, is_temp = _get_local_file_path(product.audio, "audio")
                    if audio_path and audio_path.exists():
                        # Add audio to product folder/audio - using SKU in filename
                        zip_path = f"{folder_name}/audio/{product.sku}_audio{audio_path.suffix}"
                        zipf.write(audio_path, zip_path)
                        audio_count += 1
                        
                        # Track temp file for cleanup
                        if is_temp:
                            temp_files.append(audio_path)
                except Exception as e:
                    print(f"Warning: Could not add audio {product.audio} for product {product.id}: {e}")
        else:
            # Multiple products export
            # Create a single CSV with all products
            csv_content = _create_products_csv(products)
            zipf.writestr("products.csv", csv_content)
            
            # Track temp files to clean up later
            temp_files = []
            
            # Process all products
            for product in products:
                # Create product folder with ID
                product_folder = f"product_{product.id}"
                
                # Process images
                if product.images:
                    for i, image_url in enumerate(product.images):
                        try:
                            image_path, is_temp = _get_local_file_path(image_url, "images")
                            if image_path and image_path.exists():
                                # Add images to images/product_id/ - using SKU in filename
                                zip_path = f"images/{product_folder}/{product.sku}_{i+1}{image_path.suffix}"
                                zipf.write(image_path, zip_path)
                                images_count += 1
                                
                                # Track temp file for cleanup
                                if is_temp:
                                    temp_files.append(image_path)
                        except Exception as e:
                            print(f"Warning: Could not add image {image_url} for product {product.id}: {e}")
                
                # Process audio
                if product.audio:
                    try:
                        audio_path, is_temp = _get_local_file_path(product.audio, "audio")
                        if audio_path and audio_path.exists():
                            # Add audio to audio/product_id/ - using SKU in filename
                            zip_path = f"audio/{product_folder}/{product.sku}_audio{audio_path.suffix}"
                            zipf.write(audio_path, zip_path)
                            audio_count += 1
                            
                            # Track temp file for cleanup
                            if is_temp:
                                temp_files.append(audio_path)
                    except Exception as e:
                        print(f"Warning: Could not add audio {product.audio} for product {product.id}: {e}")
    
    # Get file size
    file_size = os.path.getsize(export_path)
    
    # Create download URL
    download_url = f"{settings.BASE_URL}/static/exports/{export_filename}"
    
    # Clean up any temporary files
    for temp_file in temp_files:
        try:
            if temp_file.exists():
                os.unlink(temp_file)
                print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Warning: Could not delete temporary file {temp_file}: {e}")
    
    return {
        "filename": export_filename,
        "download_url": download_url,
        "size": file_size,
        "products_count": products_count,
        "images_count": images_count,
        "audio_count": audio_count
    }


def _create_product_csv(product: models.Product) -> str:
    """
    Creates CSV content from single product.
    
    Args:
        product: Product object
        
    Returns:
        CSV content as string
    """
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['id', 'sku', 'name', 'description', 'keywords', 'category', 'images', 'audio_description', 'audio'])
    
    # Write product data
    images_str = ';'.join(product.images) if product.images else ''
    keywords_str = ';'.join(product.keywords) if product.keywords else ''
    writer.writerow([
        product.id,
        product.sku or '',
        product.name,
        product.description or '',
        keywords_str,
        product.category or '',
        images_str,
        product.audio_description or '',
        product.audio or ''
    ])
    
    return output.getvalue()


def _create_products_csv(products: List[models.Product]) -> str:
    """
    Creates CSV content from multiple products.
    
    Args:
        products: List of Product objects
        
    Returns:
        CSV content as string
    """
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['id', 'sku', 'name', 'description', 'keywords', 'category', 'images', 'audio_description', 'audio'])
    
    # Write data for all products
    for product in products:
        images_str = ';'.join(product.images) if product.images else ''
        keywords_str = ';'.join(product.keywords) if product.keywords else ''
        writer.writerow([
            product.id,
            product.sku or '',
            product.name,
            product.description or '',
            keywords_str,
            product.category or '',
            images_str,
            product.audio_description or '',
            product.audio or ''
        ])
    
    return output.getvalue()


def _get_local_file_path(url: str, file_type: str) -> Tuple[Path, bool]:
    """
    Converts a URL to local file path. If the file doesn't exist locally, 
    it tries to download it from the URL.
    
    Args:
        url: File URL
        file_type: Type of file ('images' or 'audio')
        
    Returns:
        Tuple with (Path to local file, Boolean indicating if it's a temp file)
    """
    try:
        # Parse the URL to get the filename
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        
        # Determine local directory based on file type
        if file_type == "images":
            local_dir = settings.IMAGES_DIR
            local_path = local_dir / filename
        elif file_type == "audio":
            local_dir = settings.AUDIO_DIR
            local_path = local_dir / filename
        else:
            return None, False
        
        # Check if the file exists locally
        if local_path.exists():
            print(f"Found local file: {local_path}")
            return local_path, False
        
        # If not found locally, try to download from URL
        print(f"File not found locally, trying to download: {url}")
        
        # First, try to download directly to the expected location
        try:
            # Ensure the directory exists
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded to local path: {local_path}")
            return local_path, False
            
        except Exception as e:
            print(f"Error downloading to local path: {e}")
            
            # If direct download fails, use a temporary file
            try:
                # Create a temporary file with the proper extension
                suffix = Path(filename).suffix if Path(filename).suffix else ('.jpg' if file_type == 'images' else '.wav')
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_file_path = Path(temp_file.name)
                temp_file.close()
                
                # Download to temp file
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(temp_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Downloaded to temporary file: {temp_file_path}")
                return temp_file_path, True  # Mark as temp file so it can be cleaned up later
                
            except Exception as download_error:
                print(f"Failed to download file: {download_error}")
                return None, False
    
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None, False
