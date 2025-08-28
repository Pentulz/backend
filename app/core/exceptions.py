class ServiceException(Exception):
    """Base exception class for service layer"""

    pass


class CreateError(ServiceException):
    """Raised when a resource creation fails"""

    pass


class UpdateError(ServiceException):
    """Raised when a resource update fails"""

    pass


class DeleteError(ServiceException):
    """Raised when a resource deletion fails"""

    pass
