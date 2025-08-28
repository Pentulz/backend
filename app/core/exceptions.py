class ServiceException(Exception):
    """Base exception class for service layer"""
    pass


class ResourceNotFound(ServiceException):
    """Raised when a requested resource is not found"""
    pass


class ValidationError(ServiceException):
    """Raised when validation fails"""
    pass