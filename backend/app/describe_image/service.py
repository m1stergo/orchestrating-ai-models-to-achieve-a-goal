from app.describe_image.schemas import DescribeImageResponse
from app.describe_image.strategies.factory import ImageDescriptionStrategyFactory
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def describe_image(image_url: str, preferred_strategy: str = None) -> DescribeImageResponse:
    """
    Describe an image using the configured strategy.
    
    Args:
        image_url: URL of the image to describe
        preferred_strategy: Optional preferred strategy name ("qwen", "openai", etc.)
        
    Returns:
        DescribeImageResponse: The image description result
    """
    logger.info(f"🚀 describe_image called with image_url: {image_url}, strategy: {preferred_strategy}")
    
    try:
        # Get the appropriate strategy
        strategy = ImageDescriptionStrategyFactory.get_strategy(preferred_strategy)
        logger.info(f"📦 Using strategy: {strategy.strategy_name}")
        
        # Describe the image using the selected strategy
        result = await strategy.describe_image(image_url)
        
        # Add strategy information to the response
        result.strategy_used = strategy.strategy_name
        
        logger.info("✅ describe_image completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in describe_image: {str(e)}")
        raise


def get_available_strategies():
    """
    Get information about all available image description strategies.
    
    Returns:
        Dict with strategy information
    """
    return ImageDescriptionStrategyFactory.get_available_strategies()
