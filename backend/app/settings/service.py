from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
import logging
import httpx
from fastapi import Depends

from .models import UserSettings
from .schemas import UserSettingsCreate, UserSettingsUpdate, ModelInfo
from app.exceptions import NotFoundError, ValidationError
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing user settings."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_settings(self, user_id: str = "default") -> Optional[UserSettings]:
        """Get user settings by user_id."""
        return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    def get_or_create_user_settings(self, user_id: str = "default") -> UserSettings:
        """Get user settings or create default if not exists."""
        settings = self.get_user_settings(user_id)
        if not settings:
            settings = self.create_user_settings(
                UserSettingsCreate(user_id=user_id)
            )
        return settings
    
    def create_user_settings(self, settings_data: UserSettingsCreate) -> UserSettings:
        """Create new user settings."""
        try:
            db_settings = UserSettings(**settings_data.model_dump())
            self.db.add(db_settings)
            self.db.commit()
            self.db.refresh(db_settings)
            logger.info(f"Created settings for user: {settings_data.user_id}")
            return db_settings
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating settings: {str(e)}")
            raise ValidationError("Settings already exist for this user")
    
    def update_user_settings(self, user_id: str, settings_data: UserSettingsUpdate) -> UserSettings:
        """Update user settings."""
        settings = self.get_user_settings(user_id)
        if not settings:
            raise NotFoundError(f"Settings not found for user: {user_id}")
        
        # Validate models before updating
        update_data = settings_data.model_dump(exclude_unset=True)
        if update_data:
            self._validate_models(update_data)
        
        # Update fields
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(settings)
            logger.info(f"Updated settings for user: {user_id}")
            return settings
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating settings: {str(e)}")
            raise ValidationError("Failed to update settings")
    
    def delete_user_settings(self, user_id: str) -> bool:
        """Delete user settings."""
        settings = self.get_user_settings(user_id)
        if not settings:
            raise NotFoundError(f"Settings not found for user: {user_id}")
        
        try:
            self.db.delete(settings)
            self.db.commit()
            logger.info(f"Deleted settings for user: {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting settings: {str(e)}")
            raise ValidationError("Failed to delete settings")
    
    async def get_available_models(self) -> Dict[str, List[ModelInfo]]:
        """Get available models from microservices."""
        try:
            # Get models from describe-image service
            describe_models = await self._get_models_from_service(
                f"{settings.DESCRIBE_IMAGE_SERVICE_URL.rstrip('/')}/models"
            )
            
            # Get models from generate-description service  
            generate_models = await self._get_models_from_service(
                f"{settings.GENERATE_DESCRIPTION_SERVICE_URL.rstrip('/')}/models"
            )
            
            return {
                "describe_image_models": describe_models,
                "generate_description_models": generate_models
            }
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            # Return default models if services are not available
            return {
                "describe_image_models": self._get_default_describe_models(),
                "generate_description_models": self._get_default_generate_models()
            }
    
    async def _get_models_from_service(self, url: str) -> List[ModelInfo]:
        """Get models from a microservice."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Convert models to ModelInfo objects
                models = []
                model_list = data.get("models", [])
                
                for model in model_list:
                    models.append(ModelInfo(
                        name=model.get("name", "unknown"),
                        type=model.get("type", "unknown"),
                        provider=model.get("provider", "unknown"),
                        description=model.get("description", ""),
                        available=model.get("available", False),
                        requires_api_key=model.get("requires_api_key", False)
                    ))
                
                return models
        except Exception as e:
            logger.warning(f"Failed to get models from {url}: {str(e)}")
            return []
    
    def _get_default_describe_models(self) -> List[ModelInfo]:
        """Get default describe image models."""
        return [
            ModelInfo(
                name="openai",
                type="api",
                provider="OpenAI",
                description="OpenAI GPT-4o Vision API for image description",
                available=False,
                requires_api_key=True
            ),
            ModelInfo(
                name="gemini",
                type="api", 
                provider="Google",
                description="Google Gemini Pro Vision API for image description",
                available=False,
                requires_api_key=True
            ),
            ModelInfo(
                name="qwen",
                type="local",
                provider="Qwen",
                description="Local Qwen2.5-VL model for image description",
                available=False,
                requires_api_key=False
            )
        ]
    
    def _get_default_generate_models(self) -> List[ModelInfo]:
        """Get default generate description models."""
        return [
            ModelInfo(
                name="openai",
                type="api",
                provider="OpenAI",
                description="OpenAI GPT-4 text generation",
                available=False,
                requires_api_key=True
            ),
            ModelInfo(
                name="gemini",
                type="api",
                provider="Google", 
                description="Google Gemini Pro text generation",
                available=False,
                requires_api_key=True
            ),
            ModelInfo(
                name="mistral",
                type="local",
                provider="Mistral AI",
                description="Local Mistral-7B text generation",
                available=False,
                requires_api_key=False
            )
        ]
    
    def _validate_models(self, update_data: Dict[str, Any]) -> None:
        """Validate that models are valid."""
        valid_describe_models = ["openai", "gemini", "qwen"]
        valid_generate_models = ["openai", "gemini", "mistral"]
        
        if "describe_image_model" in update_data:
            model = update_data["describe_image_model"]
            if model not in valid_describe_models:
                raise ValidationError(f"Invalid describe_image_model: {model}. Valid options: {valid_describe_models}")
        
        if "generate_description_model" in update_data:
            model = update_data["generate_description_model"]
            if model not in valid_generate_models:
                raise ValidationError(f"Invalid generate_description_model: {model}. Valid options: {valid_generate_models}")


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """Get settings service instance."""
    return SettingsService(db)
