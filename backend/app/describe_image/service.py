from PIL import Image
from io import BytesIO
import requests
from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration
)
from qwen_vl_utils import process_vision_info
import torch
from app.describe_image.schemas import DescribeImageResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def describe_image(image_url) -> DescribeImageResponse:
    logger.info(f"🚀 describe_image called with image_url: {image_url}")
    
    try:
        logger.info("📦 Loading Qwen model...")
        qwen_model, qwen_processor = load_qwen_model()
        logger.info("✅ Qwen model loaded successfully")
        
        logger.info("🔍 Generating caption...")
        visual_caption = get_qwen_caption(image_url, qwen_model, qwen_processor)
        logger.info(f"✅ Caption generated: {visual_caption[:100]}...")
        
        response = DescribeImageResponse(
            description=visual_caption,
        )
        logger.info("✅ describe_image completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in describe_image: {str(e)}")
        raise


def get_qwen_caption(image_url, model, processor):
    logger.info(f"🖼️ Processing image from URL: {image_url}")
    image = Image.open(BytesIO(requests.get(image_url).content)).convert("RGB")
    logger.info(f"✅ Image loaded successfully, size: {image.size}")
    
    # Prepare messages in the format expected by Qwen2.5-VL
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_url,
                },
                {
                    "type": "text", 
                    "text": """
Analyze the main product in this image. Focus only on the product itself.

Then complete the following template with what you can observe from the image. If a field cannot be determined from the image alone, say "Not visible" or "Unknown".

Here is the product information:

Image description: {Insert a short but complete visual description of the item, including color, shape, material, and texture}
Product type: {What is the object?}
Material: {What is it made of?}
Keywords: {List relevant keywords that describe the item visually or functionally}
"""
                }
            ],
        }
    ]
    
    # Preparation for inference
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(model.device)
    
    # Generate the response
    logger.info("🔍 Generating caption with Qwen2.5-VL...")
    generated_ids = model.generate(**inputs, max_new_tokens=256)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    response = output_text[0] if output_text else "No description generated"
    logger.info(f"✅ Caption generated successfully")
    return response


def load_qwen_model():
    logger.info("🤖 Loading Qwen2.5-VL model...")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct", 
        torch_dtype="auto", 
        device_map="auto"
    )
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
    logger.info("✅ Qwen2.5-VL model loaded successfully")
    return model, processor