from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserSettingsBase(BaseModel):
    """Base schema for User Settings."""
    user_id: str = Field(default="default", description="User identifier")
    describe_image_strategy: str = Field(default="openai", description="Preferred strategy for image description")
    generate_description_strategy: str = Field(default="openai", description="Preferred strategy for description generation")


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating new user settings."""
    pass


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    describe_image_strategy: Optional[str] = Field(None, description="Preferred strategy for image description")
    generate_description_strategy: Optional[str] = Field(None, description="Preferred strategy for description generation")


class UserSettingsInDB(UserSettingsBase):
    """Schema for user settings in the database."""
    id: int = Field(..., description="Unique identifier for the settings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserSettingsResponse(UserSettingsInDB):
    """Schema for user settings response."""
    pass


class AvailableStrategiesResponse(BaseModel):
    """Schema for available strategies response."""
    describe_image_strategies: list[dict] = Field(..., description="Available strategies for image description")
    generate_description_strategies: list[dict] = Field(..., description="Available strategies for description generation")


class StrategyInfo(BaseModel):
    """Schema for strategy information."""
    name: str = Field(..., description="Strategy name")
    type: str = Field(..., description="Strategy type (api/local)")
    provider: str = Field(..., description="Strategy provider")
    description: str = Field(..., description="Strategy description")
    available: bool = Field(..., description="Whether strategy is currently available")
    requires_api_key: bool = Field(..., description="Whether strategy requires API key")
