from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class UserSettings(Base):
    """User settings database model for AI model preferences."""
    
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    describe_image_model = Column(String, nullable=False, default="openai")
    generate_description_model = Column(String, nullable=False, default="openai")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserSettings(id={self.id}, describe_image='{self.describe_image_model}', generate_description='{self.generate_description_model}')>"
