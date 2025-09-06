from fastapi import APIRouter
from .schemas import DescribeImageRequest, JobRequest, JobResponse
from .service import describe_image, warmup_model
from .model import ModelState
from .shared import model_instance
import logging
import uuid
import time

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=JobResponse)
async def run_job(request: JobRequest):
    """
    RunPod-compatible endpoint that executes jobs and returns RunPod format.
    """
    start_time = time.time()
    job_id = str(uuid.uuid4()) + "-u1"
    
    try:
        input_data = request.input
        action = input_data.get("action")
        
        logger.info(f"======== Qwen handler called with action: {action} ========")
        
        # Execute based on action
        if action == "inference":
            image_url = input_data.get("image_url")
            prompt = input_data.get("prompt")
            
            if not image_url:
                execution_time = int((time.time() - start_time) * 1000)
                return JobResponse(
                    id=job_id,
                    status="COMPLETED",
                    delayTime=0,
                    executionTime=execution_time,
                    workerId="qwen-worker",
                    output={
                        "status": "error",
                        "message": "image_url is required",
                        "data": ""
                    }
                )

            # Create request and call service
            request_obj = DescribeImageRequest(
                image_url=image_url,
                prompt=prompt
            )
            
            result = describe_image(request_obj)
            execution_time = int((time.time() - start_time) * 1000)
            
            return JobResponse(
                id=job_id,
                status="COMPLETED",
                delayTime=0,
                executionTime=execution_time,
                workerId="qwen-worker",
                output={
                    "status": result.status,
                    "message": result.message,
                    "data": result.data
                }
            )
            
        elif action == "warmup":
            result = warmup_model()
            execution_time = int((time.time() - start_time) * 1000)
            
            return JobResponse(
                id=job_id,
                status="COMPLETED",
                delayTime=0,
                executionTime=execution_time,
                workerId="qwen-worker",
                output={
                    "status": result.status,
                    "message": result.message,
                    "data": result.data
                }
            )
            
        else:
            execution_time = int((time.time() - start_time) * 1000)
            return JobResponse(
                id=job_id,
                status="COMPLETED",
                delayTime=0,
                executionTime=execution_time,
                workerId="qwen-worker",
                output={
                    "status": "error",
                    "message": f"Unknown action: {action}. Valid actions: warmup, inference",
                    "data": ""
                }
            )
            
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"Qwen job execution failed: {str(e)}")
        
        return JobResponse(
            id=job_id,
            status="COMPLETED",
            delayTime=0,
            executionTime=execution_time,
            workerId="qwen-worker",
            output={
                "status": "error",
                "message": str(e),
                "data": ""
            }
        )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Return job status based on current model state."""
    if model_instance.state == ModelState.LOADING:
        status = "IN_PROGRESS"
        message = "Model is currently loading"
    elif model_instance.state == ModelState.COLD:
        status = "COMPLETED"
        message = "Model is cold, needs warmup"
    elif model_instance.state == ModelState.IDDLE:
        status = "COMPLETED"
        message = "Model is ready"
    elif model_instance.state == ModelState.ERROR:
        status = "FAILED"
        message = "Model failed to load"
    else:
        status = "COMPLETED"
        message = "Unknown model state"
    
    return JobResponse(
        id=job_id,
        status=status,
        delayTime=0,
        executionTime=0,
        workerId="qwen-worker",
        output={
            "status": status.lower(),
            "message": message,
            "data": ""
        }
    )
