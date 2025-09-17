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
    audio_config = Column(JSON, nullable=True)  # Record<string, string> for audio configurations
    additional_context = Column(JSON, nullable=True)  # Array of key-value pairs for additional context
    image_description = Column(Text, nullable=True)  # Description generated from image
    vendor_url = Column(String, nullable=True)  # URL to vendor website
    vendor_context = Column(Text, nullable=True)  # Context from vendor
    selected_context_source = Column(String, nullable=True)  # Source of context (image/website)
    uploaded_image = Column(String, nullable=True)  # URL to uploaded image
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"
