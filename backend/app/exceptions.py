from fastapi import HTTPException, status


class AIModelException(HTTPException):
    """Exception raised for errors in the AI models."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class OrchestrationException(HTTPException):
    """Exception raised for errors in the orchestration process."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ValidationException(HTTPException):
    """Exception raised for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
