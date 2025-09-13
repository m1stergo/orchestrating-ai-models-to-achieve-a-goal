from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.features.products import schemas, service
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination.
    """
    products = await service.get_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    return await service.get_product(db, product_id=product_id)


@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    """
    return await service.create_product(db, product=product)


@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a product.
    """
    return await service.update_product(db, product_id=product_id, product_update=product)


@router.delete("/{product_id}", response_model=schemas.ProductResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product.
    """
    return await service.delete_product(db, product_id=product_id)
