from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import httpx
from fastapi import Depends

from .models import UserSettings
from .schemas import UserSettingsUpdate
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing global application settings."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_settings(self) -> UserSettings:
        """Get global settings or create default if not exists."""
        settings = self.db.query(UserSettings).first()
        if not settings:
            settings = UserSettings(
                describe_image_model="openai",
                generate_description_model="openai"
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
            logger.info("Created default global settings")
        return settings
    
    def update_settings(self, settings_data: UserSettingsUpdate) -> UserSettings:
        """Update global settings."""
        settings = self.get_or_create_settings()
        
        # Update only provided fields
        update_data = settings_data.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(settings, field, value)
            
            self.db.commit()
            self.db.refresh(settings)
            logger.info("Updated global settings")
            return settings
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating settings: {str(e)}")
            raise Exception("Failed to update settings")
    
    def reset_settings(self) -> UserSettings:
        """Reset settings to default values."""
        settings = self.get_or_create_settings()
        
        try:
            settings.describe_image_model = "openai"
            settings.generate_description_model = "openai"
            
            self.db.commit()
            self.db.refresh(settings)
            logger.info("Reset settings to defaults")
            return settings
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting settings: {str(e)}")
            raise Exception("Failed to reset settings")
    
    async def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models from microservices."""
        # Get models from describe-image service (with trailing slash)
        describe_models = await self._get_models_from_service(
            f"{settings.DESCRIBE_IMAGE_SERVICE_URL}/models/"
        )
        
        # Get models from generate-description service (with trailing slash)
        generate_models = await self._get_models_from_service(
            f"{settings.GENERATE_DESCRIPTION_SERVICE_URL}/models/"
        )
        
        return {
            "describe_image_models": describe_models,
            "generate_description_models": generate_models
        }
    
    async def _get_models_from_service(self, url: str) -> List[str]:
        """Get models from a microservice."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Expect all services to return array of strings: ["model1", "model2", ...]
                if isinstance(data, list):
                    # Return the array of model names directly
                    return data
                else:
                    logger.warning(f"Unexpected response format from {url}: expected array, got {type(data)}")
                    return []
        except Exception as e:
            logger.warning(f"Failed to get models from {url}: {str(e)}")
            return []

def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """Get settings service instance."""
    return SettingsService(db)
