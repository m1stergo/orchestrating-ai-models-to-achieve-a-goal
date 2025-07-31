from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
import logging
import httpx
import asyncio
from fastapi import Depends

from .models import UserSettings
from .schemas import UserSettingsCreate, UserSettingsUpdate, StrategyInfo
from app.exceptions import NotFoundError, ValidationError
from app.database import get_db

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
        
        # Validate strategies before updating
        update_data = settings_data.model_dump(exclude_unset=True)
        if update_data:
            self._validate_strategies(update_data)
        
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
    
    async def get_available_strategies(self) -> Dict[str, List[StrategyInfo]]:
        """Get available strategies from microservices."""
        try:
            # Get strategies from describe-image service
            describe_strategies = await self._get_strategies_from_service(
                "http://localhost:8001/api/v1/strategies"
            )
            
            # Get strategies from generate-description service  
            generate_strategies = await self._get_strategies_from_service(
                "http://localhost:8003/api/v1/strategies"
            )
            
            return {
                "describe_image_strategies": describe_strategies,
                "generate_description_strategies": generate_strategies
            }
        except Exception as e:
            logger.error(f"Error getting available strategies: {str(e)}")
            # Return default strategies if services are not available
            return {
                "describe_image_strategies": self._get_default_describe_strategies(),
                "generate_description_strategies": self._get_default_generate_strategies()
            }
    
    async def _get_strategies_from_service(self, url: str) -> List[StrategyInfo]:
        """Get strategies from a microservice."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Convert strategies to StrategyInfo objects
                strategies = []
                strategy_list = data.get("strategies", [])
                
                for strategy in strategy_list:
                    strategies.append(StrategyInfo(
                        name=strategy.get("name", "unknown"),
                        type=strategy.get("type", "unknown"),
                        provider=strategy.get("provider", "unknown"),
                        description=strategy.get("description", ""),
                        available=strategy.get("available", False),
                        requires_api_key=strategy.get("requires_api_key", False)
                    ))
                
                return strategies
        except Exception as e:
            logger.warning(f"Failed to get strategies from {url}: {str(e)}")
            return []
    
    def _get_default_describe_strategies(self) -> List[StrategyInfo]:
        """Get default describe image strategies."""
        return [
            StrategyInfo(
                name="openai",
                type="api",
                provider="OpenAI",
                description="OpenAI GPT-4o Vision API for image description",
                available=False,
                requires_api_key=True
            ),
            StrategyInfo(
                name="gemini",
                type="api", 
                provider="Google",
                description="Google Gemini Pro Vision API for image description",
                available=False,
                requires_api_key=True
            ),
            StrategyInfo(
                name="qwen",
                type="local",
                provider="Qwen",
                description="Local Qwen2.5-VL model for image description",
                available=False,
                requires_api_key=False
            )
        ]
    
    def _get_default_generate_strategies(self) -> List[StrategyInfo]:
        """Get default generate description strategies."""
        return [
            StrategyInfo(
                name="openai",
                type="api",
                provider="OpenAI",
                description="OpenAI GPT-4 text generation",
                available=False,
                requires_api_key=True
            ),
            StrategyInfo(
                name="gemini",
                type="api",
                provider="Google", 
                description="Google Gemini Pro text generation",
                available=False,
                requires_api_key=True
            ),
            StrategyInfo(
                name="mistral",
                type="local",
                provider="Mistral AI",
                description="Local Mistral-7B text generation",
                available=False,
                requires_api_key=False
            )
        ]
    
    def _validate_strategies(self, update_data: Dict[str, Any]) -> None:
        """Validate that strategies are valid."""
        valid_describe_strategies = ["openai", "gemini", "qwen"]
        valid_generate_strategies = ["openai", "gemini", "mistral"]
        
        if "describe_image_strategy" in update_data:
            strategy = update_data["describe_image_strategy"]
            if strategy not in valid_describe_strategies:
                raise ValidationError(f"Invalid describe_image_strategy: {strategy}. Valid options: {valid_describe_strategies}")
        
        if "generate_description_strategy" in update_data:
            strategy = update_data["generate_description_strategy"]
            if strategy not in valid_generate_strategies:
                raise ValidationError(f"Invalid generate_description_strategy: {strategy}. Valid options: {valid_generate_strategies}")


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """Get settings service instance."""
    return SettingsService(db)
