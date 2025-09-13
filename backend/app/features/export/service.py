import os
import csv
import zipfile
import uuid
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.features.products.models import Product


async def create_export_zip(db: Session, product_id: int) -> dict:
    """
    Creates a ZIP file containing single product data: images, audio files, and CSV.
    
    Args:
        db: Database session
        product_id: ID of the product to export
        
    Returns:
        Dictionary with export information
    """
    # Get specific product from database
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    # Create temporary directory for export
    export_dir = settings.EXPORTS_DIR
    export_dir.mkdir(exist_ok=True)
    
    # Generate unique filename for the export
    export_filename = f"product_{product_id}_export_{uuid.uuid4().hex[:8]}.zip"
    export_path = export_dir / export_filename
    
    images_count = 0
    audio_count = 0
    
    # Create folder name using product SKU and name
    # Clean product name for filesystem compatibility
    clean_name = "".join(c for c in product.name if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_name = clean_name.replace(' ', '_')
    folder_name = f"{product.sku}_{clean_name}"
    
    with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Create CSV with product data
        csv_content = _create_product_csv(product)
        zipf.writestr(f"{folder_name}/product.csv", csv_content)
        
        # Process images
        if product.images:
            for i, image_url in enumerate(product.images):
                try:
                    image_path = _get_local_file_path(image_url, "images")
                    if image_path and image_path.exists():
                        # Add images to product folder/images
                        zip_path = f"{folder_name}/images/image_{i+1}{image_path.suffix}"
                        zipf.write(image_path, zip_path)
                        images_count += 1
                except Exception as e:
                    print(f"Warning: Could not add image {image_url} for product {product.id}: {e}")
        
        # Process audio
        if product.audio:
            try:
                audio_path = _get_local_file_path(product.audio, "audio")
                if audio_path and audio_path.exists():
                    # Add audio to product folder/audio
                    zip_path = f"{folder_name}/audio/audio{audio_path.suffix}"
                    zipf.write(audio_path, zip_path)
                    audio_count += 1
            except Exception as e:
                print(f"Warning: Could not add audio {product.audio} for product {product.id}: {e}")
    
    # Get file size
    file_size = os.path.getsize(export_path)
    
    # Create download URL
    download_url = f"{settings.BASE_URL}/static/exports/{export_filename}"
    
    return {
        "url": download_url
    }


def _create_product_csv(product: Product) -> str:
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


def _get_local_file_path(url: str, file_type: str) -> Path:
    """
    Converts a URL to local file path.
    
    Args:
        url: File URL
        file_type: Type of file ('images' or 'audio')
        
    Returns:
        Path to local file
    """
    try:
        # Parse the URL to get the filename
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        
        if file_type == "images":
            return settings.IMAGES_DIR / filename
        elif file_type == "audio":
            return settings.AUDIO_DIR / filename
        else:
            return None
    except Exception:
        return None
