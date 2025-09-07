from fastapi import APIRouter
from .schemas import GenerateDescriptionRequest, JobRequest, JobResponse
from .service import generate_description, check_job_status, warmup_model
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/run", response_model=JobResponse)
async def run_job(request: JobRequest):
    """
    RunPod-compatible endpoint that executes jobs and returns RunPod format.
    """
    job_id = str(uuid.uuid4()) + "-u1"
    
    try:
        input_data = request.input
        action = input_data.get("action")
        
        logger.info(f"======== Mistral handler called with action: {action} ========")
        
        # Execute based on action
        if action == "inference":
            text = input_data.get("text")
            prompt = input_data.get("prompt")
            
            if not text:
                return JobResponse(
                    id=job_id,
                    status="ERROR",
                    workerId="mistral-worker",
                    details=JobDetails(
                        status="ERROR",
                        message="text is required",
                        data=""
                    )
                )

            # Create request and call service
            request_obj = GenerateDescriptionRequest(
                text=text,
                prompt=prompt
            )
            
            # generate_description ahora devuelve directamente un JobResponse
            result = generate_description(request_obj)
            
            # Simplemente devolvemos el resultado con el id del job_id
            return JobResponse(
                id=job_id,
                status=result.status,
                workerId="mistral-worker",
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
                workerId="mistral-worker",
                details=JobDetails(
                    status="ERROR",
                    message=f"Unknown action: {action}. Valid actions: warmup, inference",
                    data=""
                )
            )
            
    except Exception as e:
        logger.error(f"Mistral job execution failed: {str(e)}")
        
        return JobResponse(
            id=job_id,
            status="ERROR",
            workerId="mistral-worker",
            details=JobDetails(
                status="ERROR",
                message=str(e),
                data=""
            )
        )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Return current status of a previously submitted job."""
    return check_job_status(job_id)