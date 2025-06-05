"""
Exceptions HTTP personnalisées pour l'API.
Centralise les messages d'erreur standards.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Exception pour ressource non trouvée."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedException(HTTPException):
    """Exception pour accès non autorisé."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """Exception pour accès interdit."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class BadRequestException(HTTPException):
    """Exception pour requête invalide."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ConflictException(HTTPException):
    """Exception pour conflit de données."""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )