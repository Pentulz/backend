class ServiceException(Exception):
    """Base exception class for service layer"""


class CreateError(ServiceException):
    """Raised when a resource creation fails"""


class UpdateError(ServiceException):
    """Raised when a resource update fails"""


class DeleteError(ServiceException):
    """Raised when a resource deletion fails"""
