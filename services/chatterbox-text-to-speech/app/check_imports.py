#!/usr/bin/env python
"""
Script to verify that all the necessary dependencies for ChatterboxTTS
are imported correctly before starting the service.
"""
import sys
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check_imports")


try:
    logger.info("Verifying torch import...")
    import torch
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    
    logger.info("Verifying torchvision import...")
    import torchvision
    logger.info(f"Torchvision version: {torchvision.__version__}")
    
    # Verify that torchvision.ops.nms is available
    logger.info("Verifying torchvision.ops.nms...")
    from torchvision.ops import nms
    logger.info("nms operator available!")
    
    logger.info("Verifying transformers import...")
    from transformers import LlamaModel, LlamaConfig
    logger.info("LlamaModel imported correctly!")
    
    logger.info("Verifying ChatterboxTTS import...")
    from chatterbox.tts import ChatterboxTTS
    logger.info("ChatterboxTTS imported correctly!")
    
    logger.info("All imports were successful!")
    sys.exit(0)
except Exception as e:
    logger.error(f"Error during import: {str(e)}")
    logger.exception("Error details:")
    sys.exit(1)