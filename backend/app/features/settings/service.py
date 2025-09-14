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
    
    def _get_db_settings(self) -> UserSettings:
        """Get settings from database or create default if not exists."""
        db_settings = self.db.query(UserSettings).first()
        if not db_settings:
            db_settings = UserSettings(
                describe_image_model="openai",
                generate_description_model="openai"
            )
            self.db.add(db_settings)
            self.db.commit()
            self.db.refresh(db_settings)
            logger.info("Created default settings")
        return db_settings
        
    async def get_settings_with_models(self) -> dict:
        """Get settings with available models."""
        # Get settings from database
        db_settings = self._get_db_settings()
        
        # Get available models from services
        models = await self._fetch_available_models()
        
        # Convert settings to dict and add models
        return {
            "id": db_settings.id,
            "describe_image_model": db_settings.describe_image_model,
            "generate_description_model": db_settings.generate_description_model,
            "describe_image_prompt": db_settings.describe_image_prompt,
            "generate_description_prompt": db_settings.generate_description_prompt,
            "generate_promotional_audio_script_prompt": db_settings.generate_promotional_audio_script_prompt,
            "categories": db_settings.categories,
            "created_at": db_settings.created_at,
            "updated_at": db_settings.updated_at,
            "describe_image_models": models["describe_image_models"],
            "generate_description_models": models["generate_description_models"]
        }
        
    def update_settings(self, settings_data: UserSettingsUpdate) -> dict:
        """Update settings and return the updated values."""
        # Update the settings in database
        db_settings = self._update_db_settings(settings_data)
        
        # Convert to dict for response
        return {
            "id": db_settings.id,
            "describe_image_model": db_settings.describe_image_model,
            "generate_description_model": db_settings.generate_description_model,
            "describe_image_prompt": db_settings.describe_image_prompt,
            "generate_description_prompt": db_settings.generate_description_prompt,
            "generate_promotional_audio_script_prompt": db_settings.generate_promotional_audio_script_prompt,
            "categories": db_settings.categories,
            "created_at": db_settings.created_at,
            "updated_at": db_settings.updated_at
        }
        
    def reset_settings(self) -> None:
        """Reset settings to default values."""
        db_settings = self._get_db_settings()
        
        try:
            db_settings.describe_image_model = "openai"
            db_settings.generate_description_model = "openai"
            db_settings.describe_image_prompt = None
            db_settings.generate_description_prompt = None
            db_settings.generate_promotional_audio_script_prompt = None
            db_settings.categories = None
            
            self.db.commit()
            self.db.refresh(db_settings)
            logger.info("Reset settings to defaults")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting settings: {str(e)}")
            raise Exception("Failed to reset settings")
    
    def _update_db_settings(self, settings_data: UserSettingsUpdate) -> UserSettings:
        """Update settings in database."""
        db_settings = self._get_db_settings()
        
        # Update only provided fields
        update_data = settings_data.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(db_settings, field, value)
            
            self.db.commit()
            self.db.refresh(db_settings)
            logger.info("Updated settings")
            return db_settings
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating settings: {str(e)}")
            raise Exception("Failed to update settings")
    
    async def _fetch_available_models(self) -> Dict[str, List[str]]:
        """Fetch available models from internal backend services."""
        # Get models from describe_image service (internal backend endpoint)
        describe_models = await self._get_models_from_service(
            f"{settings.BASE_URL}{settings.API_VERSION}/describe-image/models"
        )
        
        # Get models from generate_description service (internal backend endpoint)
        generate_models = await self._get_models_from_service(
            f"{settings.BASE_URL}{settings.API_VERSION}/generate-description/models"
        )

        logger.info(f"===== Available describe_image models: {describe_models} =====")
        logger.info(f"===== Available generate_description models: {generate_models} =====")
        
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
                r = response.json()
                data = r["data"]
                
                if isinstance(data, list):
                    return data
                else:
                    logger.warning(f"Unexpected response format from {url}: {data}")
                    return []
        except Exception as e:
            logger.warning(f"Failed to get models from {url}: {str(e)}")
            return []

def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """Get settings service instance."""
    return SettingsService(db)
