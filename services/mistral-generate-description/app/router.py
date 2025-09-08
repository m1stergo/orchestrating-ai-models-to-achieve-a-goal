from fastapi import APIRouter
from .schemas import GenerateDescriptionRequest, JobRequest, JobResponse
from .service import generate_description, check_job_status, warmup_model
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=JobResponse)
async def run_job(request: JobRequest):
    """
    RunPod-compatible endpoint that executes jobs and returns RunPod format.
    """
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
                    id="none",
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
            
            # generate_description devuelve directamente un JobResponse
            job_response = generate_description(request_obj)
            
            # Simplemente devolvemos la respuesta tal cual
            return job_response
            
        elif action == "warmup":
            # Warmup model now returns a JobResponse directly with the correct status
            result = warmup_model()
            # Simply return the warmup result directly
            return result
            
        else:
            return JobResponse(
                id="none",
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
            id="none",
            status="ERROR",
            workerId="mistral-worker",
            details=JobDetails(
                status="ERROR",
                message=str(e),
                data=""
            )
        )


@router.get("/status/{id}")
async def get_job_status(id: str):
    """Return current status of a previously submitted job."""
    return check_job_status(id)