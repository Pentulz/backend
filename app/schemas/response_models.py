from typing import Any, Dict, List

from pydantic import BaseModel, Field

# Response models for different endpoints


class MessageAttributes(BaseModel):
    """Message attributes for response model"""

    message: str = Field(..., description="Response message")


class MessageResponse(BaseModel):
    """Response model for simple message responses"""

    data: MessageAttributes = Field(..., description="Message data in JSON:API format")


class ToolsResponse(BaseModel):
    """Response model for tools endpoint"""

    data: List[Dict[str, Any]] = Field(..., description="List of available tools")


class ErrorResponse(BaseModel):
    """Error response model"""

    errors: List[Dict[str, str]] = Field(..., description="List of error details")


# Specific error response models for different HTTP status codes
class BadRequestError(BaseModel):
    """400 Bad Request error response"""

    errors: List[Dict[str, str]] = Field(..., description="List of validation errors")


class NotFoundError(BaseModel):
    """404 Not Found error response"""

    errors: List[Dict[str, str]] = Field(..., description="List of not found errors")


class InternalServerError(BaseModel):
    """500 Internal Server Error response"""

    errors: List[Dict[str, str]] = Field(..., description="List of server errors")


class UnauthorizedError(BaseModel):
    """401 Unauthorized error response"""

    errors: List[Dict[str, str]] = Field(
        ..., description="List of authentication errors"
    )


class ForbiddenError(BaseModel):
    """403 Forbidden error response"""

    errors: List[Dict[str, str]] = Field(..., description="List of permission errors")


class ConflictError(BaseModel):
    """409 Conflict error response"""

    errors: List[Dict[str, str]] = Field(..., description="List of conflict errors")


# Detailed error structure models
class ErrorDetail(BaseModel):
    """Individual error detail following JSON:API spec"""

    status: str = Field(..., description="HTTP status code as string")
    title: str = Field(..., description="Error title")
    detail: str = Field(..., description="Detailed error message")


class DetailedErrorResponse(BaseModel):
    """Detailed error response with proper JSON:API structure"""

    errors: List[ErrorDetail] = Field(..., description="List of detailed errors")


# Specific detailed error responses
class DetailedBadRequestError(BaseModel):
    """400 Bad Request error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of validation errors")


class DetailedNotFoundError(BaseModel):
    """404 Not Found error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of not found errors")


class DetailedInternalServerError(BaseModel):
    """500 Internal Server Error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of server errors")


class DetailedUnauthorizedError(BaseModel):
    """401 Unauthorized error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of authentication errors")


class DetailedForbiddenError(BaseModel):
    """403 Forbidden error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of permission errors")


class DetailedConflictError(BaseModel):
    """409 Conflict error response with detailed structure"""

    errors: List[ErrorDetail] = Field(..., description="List of conflict errors")
