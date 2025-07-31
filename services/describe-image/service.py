import logging
from typing import List, Dict

from schemas import DescribeImageRequest, DescribeImageResponse
from strategies.factory import ImageDescriptionStrategyFactory

logger = logging.getLogger(__name__)

async def describe_image(
    request: DescribeImageRequest
) -> DescribeImageResponse:
    """
    Describe an image using the specified or best available strategy.
    
    Args:
        request: The image description request containing image_url and optional strategy
        
    Returns:
        DescribeImageResponse: The image description result with strategy_used
    """
    try:
        # Get strategy from request
        strategy = ImageDescriptionStrategyFactory.get_strategy(request.strategy)
        logger.info(f"Using strategy: {strategy.strategy_name}")
        
        # Check if strategy is available
        if not strategy.is_available():
            raise Exception(f"Strategy {strategy.strategy_name} is not available")
        
        # Describe the image using the selected strategy
        result = await strategy.describe_image(request.image_url)
        
        # Add strategy information to the response
        result.strategy_used = strategy.strategy_name
        
        logger.info("✅ Image description completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")


async def get_available_strategies() -> List[Dict]:
    """
    Get information about all available image description strategies.
    
    Returns:
        List of strategy information dictionaries
    """
    try:
        strategies_dict = ImageDescriptionStrategyFactory.get_available_strategies()
        # Convert dict to list format to match generate-description pattern
        strategies_list = []
        for name, info in strategies_dict.items():
            strategy_info = info.copy()
            strategy_info['name'] = name
            strategies_list.append(strategy_info)
        return strategies_list
    except Exception as e:
        logger.error(f"Error getting available strategies: {str(e)}")
        return []
