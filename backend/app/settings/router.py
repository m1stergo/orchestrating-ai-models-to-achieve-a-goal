from fastapi import APIRouter, Depends, HTTPException, status
import logging

from .service import get_settings_service, SettingsService
from .schemas import (
    UserSettingsResponse, 
    UserSettingsUpdate,
    AvailableModelsResponse
)
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get all available models for both services."""
    try:
        models = await settings_service.get_available_models()
        return AvailableModelsResponse(**models)
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )

@router.get("/", response_model=UserSettingsResponse)
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get global application settings."""
    try:
        settings = settings_service.get_or_create_user_settings("default")
        return UserSettingsResponse.model_validate(settings)
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get settings"
        )

@router.put("/", response_model=UserSettingsResponse)
async def update_settings(
    settings_data: UserSettingsUpdate,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update global application settings."""
    try:
        settings = settings_service.update_user_settings("default", settings_data)
        return UserSettingsResponse.model_validate(settings)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def reset_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Reset settings to default values."""
    try:
        settings_service.delete_user_settings("default")
        return None
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset settings"
        )