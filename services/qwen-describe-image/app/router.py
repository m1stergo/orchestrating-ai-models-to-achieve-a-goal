from fastapi import APIRouter
from typing import Dict, Any
from .common import JobResponse
import logging
from .shared import handler
from .common import RunPodSimulator

router = APIRouter()
logger = logging.getLogger(__name__)

pod = RunPodSimulator(handler)

@router.post("/run", response_model=JobResponse)
async def run(request: Dict[str, Any]):
    input_data = request.get('input', request)
    return pod.run(input_data)

@router.get("/status/{id}")
async def status(id: str):
    return pod.status(id)
