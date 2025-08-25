from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.products import models, schemas


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
        audio=product.audio
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
