from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from .service import get_settings_service, SettingsService
from .schemas import (
    UserSettingsResponse, 
    UserSettingsCreate, 
    UserSettingsUpdate,
    AvailableStrategiesResponse
)
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("/strategies", response_model=AvailableStrategiesResponse)
async def get_available_strategies(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get all available strategies for both services."""
    try:
        strategies = await settings_service.get_available_strategies()
        return AvailableStrategiesResponse(**strategies)
    except Exception as e:
        logger.error(f"Error getting available strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available strategies"
        )


@router.get("/{user_id}", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: str = "default",
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user settings by user_id."""
    try:
        settings = settings_service.get_or_create_user_settings(user_id)
        return UserSettingsResponse.model_validate(settings)
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user settings"
        )


@router.post("/", response_model=UserSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_user_settings(
    settings_data: UserSettingsCreate,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Create new user settings."""
    try:
        settings = settings_service.create_user_settings(settings_data)
        return UserSettingsResponse.model_validate(settings)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user settings"
        )


@router.put("/{user_id}", response_model=UserSettingsResponse)
async def update_user_settings(
    user_id: str,
    settings_data: UserSettingsUpdate,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user settings."""
    try:
        settings = settings_service.update_user_settings(user_id, settings_data)
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
        logger.error(f"Error updating user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Delete user settings."""
    try:
        settings_service.delete_user_settings(user_id)
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
        logger.error(f"Error deleting user settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user settings"
        )


@router.get("/", response_model=UserSettingsResponse)
async def get_default_user_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get default user settings (convenience endpoint)."""
    return await get_user_settings("default", settings_service)
