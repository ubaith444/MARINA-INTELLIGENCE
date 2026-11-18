"""Custom Application & Domain Exceptions."""

from typing import Any, Optional


class MarinaException(Exception):
    """Base domain exception for Marina Intelligence."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class EntityNotFoundError(MarinaException):
    """Raised when a requested domain entity is not found."""
    pass


class IntegrityConstraintViolationError(MarinaException):
    """Raised when an operation violates football data integrity or business rules."""
    pass


class FabricatedDataViolationError(IntegrityConstraintViolationError):
    """Raised when an attempt is made to fabricate statistics or match results."""
    pass
