from fastapi import APIRouter
from .schemas import DescribeImageRequest, JobRequest, JobResponse, DescribeImageDetails, JobStatus
from .service import describe_image, warmup_model, check_job_status
from .model import ModelState
from .shared import model_instance
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=JobResponse)
async def run_job(request: JobRequest):
    """
    RunPod-compatible endpoint that executes jobs and returns RunPod format.
    """
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
                return JobResponse(
                    id=job_id,
                    status="ERROR",
                    workerId="qwen-worker",
                    details=DescribeImageDetails(
                        status="ERROR",
                        message="image_url is required",
                        data=""
                    )
                )

            # Create request and call service
            request_obj = DescribeImageRequest(
                image_url=image_url,
                prompt=prompt
            )
            
            # describe_image ahora devuelve directamente un JobResponse
            result = describe_image(request_obj)
            
            # Simplemente devolvemos el resultado con el id del job_id
            return JobResponse(
                id=job_id,
                status=result.status,
                workerId="qwen-worker",
                details=result.details
            )
            
        elif action == "warmup":
            # Warmup model now returns a JobResponse directly with the correct status
            result = warmup_model()
            # Simply return the warmup result directly
            return result
            
        else:
            return JobResponse(
                id=job_id,
                status="ERROR",
                workerId="qwen-worker",
                details=DescribeImageDetails(
                    status="ERROR",
                    message=f"Unknown action: {action}. Valid actions: warmup, inference",
                    data=""
                )
            )
            
    except Exception as e:
        logger.error(f"Qwen job execution failed: {str(e)}")
        
        return JobResponse(
            id=job_id,
            status="ERROR",
            workerId="qwen-worker",
            details=DescribeImageDetails(
                status="ERROR",
                message=str(e),
                data=""
            )
        )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Return current status of a previously submitted job."""
    # Usar la nueva función de verificación de estado
    return check_job_status(job_id)
