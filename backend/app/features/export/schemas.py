from pydantic import BaseModel
from typing import Optional


class ExportResponse(BaseModel):
    """Response schema for export operations."""
    
    url: str
