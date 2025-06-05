"""Exceptions personnalisées."""
from .http import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    ConflictException
)

__all__ = [
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "BadRequestException",
    "ConflictException"
]