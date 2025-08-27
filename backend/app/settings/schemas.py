from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserSettingsBase(BaseModel):
    """Base schema for User Settings."""
    describe_image_model: str = Field(default="openai", description="Preferred model for image description")
    generate_description_model: str = Field(default="openai", description="Preferred model for description generation")
    generate_description_prompt: Optional[str] = Field(None, description="Custom prompt for product description generation")
    generate_promotional_audio_script_prompt: Optional[str] = Field(None, description="Custom prompt for promotional audio script generation")
    categories: Optional[List[str]] = Field(None, description="Available product categories")


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating new user settings."""
    pass


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    describe_image_model: Optional[str] = Field(None, description="Preferred model for image description")
    generate_description_model: Optional[str] = Field(None, description="Preferred model for description generation")
    generate_description_prompt: Optional[str] = Field(None, description="Custom prompt for product description generation")
    generate_promotional_audio_script_prompt: Optional[str] = Field(None, description="Custom prompt for promotional audio script generation")
    categories: Optional[List[str]] = Field(None, description="Available product categories")


class UserSettingsInDB(UserSettingsBase):
    """Schema for user settings in the database."""
    id: int = Field(..., description="Unique identifier for the settings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserSettingsResponse(UserSettingsInDB):
    """Schema for user settings response with available models."""
    describe_image_models: list[str] = Field(default_factory=list, description="Available model names for image description")
    generate_description_models: list[str] = Field(default_factory=list, description="Available model names for description generation")


class AvailableModelsResponse(BaseModel):
    """Schema for available models response."""
    describe_image_models: list[str] = Field(..., description="Available model names for image description")
    generate_description_models: list[str] = Field(..., description="Available model names for description generation")
