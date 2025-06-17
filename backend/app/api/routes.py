from fastapi import APIRouter
from app.models.request_models import PipelineInput
from app.models.response_models import PipelineOutput

router = APIRouter()

@router.post("/run-pipeline", response_model=PipelineOutput)
async def run_pipeline(input: PipelineInput):
    return ''
