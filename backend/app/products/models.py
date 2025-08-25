from sqlalchemy import Column, Integer, String, JSON, Text
from app.database import Base


class Product(Base):
    """Product database model."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # Array of keyword strings
    category = Column(String, nullable=True)
    images = Column(JSON, nullable=True)  # Array of URL strings
    audio_description = Column(Text, nullable=True)
    audio = Column(String, nullable=True)  # URL string
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"
