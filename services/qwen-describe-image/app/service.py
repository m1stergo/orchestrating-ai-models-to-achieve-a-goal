import logging
import asyncio
import torch

from .schemas import DescribeImageRequest, DescribeImageResponse
from .shared import model_instance, model_loaded

logger = logging.getLogger(__name__)

# Semaphore to limit concurrent inference requests
# Adjust the value based on your GPU memory and model requirements
MAX_CONCURRENT_INFERENCES = 1
semaphore = asyncio.Semaphore(MAX_CONCURRENT_INFERENCES)


async def describe_image(request: DescribeImageRequest) -> DescribeImageResponse:
    """
    Describe an image using the preloaded adapter with concurrency control.
    
    Args:
        request: The image description request containing image_url and optional prompt
        
    Returns:
        DescribeImageResponse: The image description result
    """
    global model_instance, model_loaded
    
    try:
        # Check if model is loaded
        if not model_loaded:
            logger.warning("Model not loaded yet, attempting to load")
            try:
                await model_instance.is_loaded()
                model_loaded = True
            except Exception as e:
                logger.error(f"Failed to load model on demand: {str(e)}")
                return DescribeImageResponse(description="Model not loaded and failed to load on demand")
        
        # Use semaphore to limit concurrent inferences
        async with semaphore:
            logger.info(f"Processing image from URL: {request.image_url}")
            # Use the global model instance
            result = await model_instance.describe_image(request.image_url, request.prompt)
        logger.info("Image description completed successfully")
        return DescribeImageResponse(description=result)
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}")
        raise Exception(f"Image description failed: {str(e)}")


def get_gpu_info():
    """
    Get information about available GPUs using PyTorch.
    
    Returns:
        dict: Dictionary containing GPU information
    """
    # Get GPU information
    cuda_available = torch.cuda.is_available()
    gpu_info = {}
    
    if cuda_available:
        gpu_count = torch.cuda.device_count()
        gpu_info = {
            "cuda_available": True,
            "cuda_version": torch.version.cuda,
            "gpu_count": gpu_count,
            "devices": []
        }
        
        # Get info for each GPU
        for i in range(gpu_count):
            device_name = torch.cuda.get_device_name(i)
            device_capability = torch.cuda.get_device_capability(i)
            total_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)  # Convert to GB
            
            gpu_info["devices"].append({
                "index": i,
                "name": device_name,
                "compute_capability": f"{device_capability[0]}.{device_capability[1]}",
                "total_memory_gb": f"{total_memory:.2f}"
            })
    else:
        gpu_info = {"cuda_available": False}
    
    return gpu_info


def get_service_status():
    """
    Get the current service status including model loading state and GPU information.
    
    Returns:
        dict: Dictionary containing service status information
    """
    return {
        "status": "ready" if model_loaded else "loading",
        "loaded": model_loaded,
        "service": "describe-image",
        "gpu": get_gpu_info()
    }


async def warmup_model():
    """
    Trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    
    Returns:
        dict: Status of the warmup operation
    """
    import logging
    logger = logging.getLogger(__name__)
    
    global model_instance, model_loaded
    
    if model_loaded:
        logger.info("Model already loaded")
        return {"status": "already_loaded", "loaded": True}
    
    try:
        logger.info("Starting model warmup...")
        await model_instance.is_loaded()
        
        # Update the global model_loaded flag
        import app.shared as shared
        shared.model_loaded = True
        model_loaded = True
        
        logger.info("Model warmup completed successfully")
        return {"status": "loaded_successfully", "loaded": True}
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")
        raise Exception(f"Failed to load model: {str(e)}")
