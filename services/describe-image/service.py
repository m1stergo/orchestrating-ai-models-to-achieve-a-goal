import logging
from typing import List, Dict

from schemas import DescribeImageRequest, DescribeImageResponse
from ai_models.factory import ImageDescriptionModelFactory

logger = logging.getLogger(__name__)

async def describe_image(
    request: DescribeImageRequest
) -> DescribeImageResponse:
    """
    Describe an image using the specified or best available model.
    
    Args:
        request: The image description request containing image_url and optional model
        
    Returns:
        DescribeImageResponse: The image description result with model_used
    """
    try:
        # Get model from request
        model = ImageDescriptionModelFactory.get_model(request.model)
        logger.info(f"Using model: {model.model_name}")
        
        # Check if model is available
        if not model.is_available():
            raise Exception(f"Model {model.model_name} is not available")
        
        # Describe the image using the selected model
        result = await model.describe_image(request.image_url)
        
        logger.info("Image description completed successfully")
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")


async def get_available_models() -> List[Dict]:
    """
    Get information about all available image description models.
    
    Returns:
        List of dictionaries containing model information
    """
    try:
        models_dict = ImageDescriptionModelFactory.get_available_models()
        
        models_list = []
        for name, info in models_dict.items():
            model_info = {"name": name, **info}
            models_list.append(model_info)
        return models_list
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        return []
