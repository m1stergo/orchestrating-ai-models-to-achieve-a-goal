"""Custom exceptions for the application.

This module defines custom exception classes that extend FastAPI's HTTPException
to provide standardized error handling throughout the application. Each exception
class is associated with a specific HTTP status code and can be used to raise
appropriate errors in different contexts.

Classes:
    AIModelException: For errors in AI model operations
    OrchestrationException: For errors in the orchestration process
    ValidationException: For input validation errors
    NotFoundError: For resource not found errors
    ValidationError: For data validation errors (alternative to ValidationException)
"""

from fastapi import HTTPException, status


class AIModelException(HTTPException):
    """Exception raised for errors in the AI models.
    
    This exception should be used when an AI model (e.g., OpenAI, Gemini, Mistral)
    fails to process a request or returns an error. It results in a 500 Internal
    Server Error response.
    
    Args:
        detail: A description of the error that occurred
    """
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class OrchestrationException(HTTPException):
    """Exception raised for errors in the orchestration process.
    
    This exception should be used when there's an error in the process of
    orchestrating multiple services or components together. For example,
    when coordinating calls between different AI services. It results in
    a 500 Internal Server Error response.
    
    Args:
        detail: A description of the error that occurred
    """
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ValidationException(HTTPException):
    """Exception raised for validation errors.
    
    This exception should be used when input data fails validation rules
    that are not automatically caught by Pydantic schemas. It results in
    a 400 Bad Request response.
    
    Args:
        detail: A description of the validation error
    """
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class NotFoundError(HTTPException):
    """Exception raised when a resource is not found.
    
    This exception should be used when a requested resource (e.g., a product,
    an image, a setting) cannot be found in the database or storage. It results
    in a 404 Not Found response.
    
    Args:
        detail: A description of what resource was not found
    """
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationError(HTTPException):
    """Exception raised for validation errors (alternative to ValidationException).
    
    This exception serves the same purpose as ValidationException and is provided
    for backward compatibility or preference. It results in a 400 Bad Request response.
    
    Note:
        It's recommended to standardize on either ValidationException or ValidationError
        throughout the codebase to maintain consistency.
    
    Args:
        detail: A description of the validation error
    """
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
