from app.describe_image.schemas import DescribeImageResponse


async def describe_image(image_url, prompt) -> DescribeImageResponse:
    """
    Mock function to describe an image using Qwen.
    In a real implementation, this would use the Qwen API or SDK.
    
    Args:
        image_url: URL of the image to analyze
        prompt: The prompt to generate the description
        
    Returns:
        DescribeImageResponse: The description results
    """
    # Mock response
    
    return DescribeImageResponse(
        description="A person standing next to a car in an urban environment",
    )
