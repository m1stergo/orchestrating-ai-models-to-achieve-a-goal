from fastapi import APIRouter
from typing import Dict, Any
from .common import JobResponse
import logging
from .shared import handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", response_model=JobResponse)
async def run(request: Dict[str, Any]):
    input_data = request.get('input', request)
    
    if 'action' not in input_data:
        logger.warning(f"==== Missing 'action' in input_data, adding default 'inference' action ====")
        input_data['action'] = 'inference'
    
    return handler.run_job(input_data)


@router.get("/status/{id}")
async def get_job_status(id: str):
    return handler.check_job_status(id)