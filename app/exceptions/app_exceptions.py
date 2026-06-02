class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found.",
            status_code=404,
        )


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class BadRequestException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class InsufficientStockException(AppException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            message=(
                f"Insufficient stock for '{product_name}'. "
                f"Available: {available}, Requested: {requested}."
            ),
            status_code=422,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Not authenticated."):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message=message, status_code=403)
