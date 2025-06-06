"""
Dépendances FastAPI réutilisables.
Gère l'authentification et les permissions.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.models.user import User
from app.schemas.user import TokenData
from app.utils.security import decode_access_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Schéma OAuth2 pour l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme)
) -> User:
    """
    Récupère l'utilisateur actuel depuis le token JWT.

    Args:
        token: Token JWT depuis l'en-tête Authorization

    Returns:
        User: Utilisateur authentifié

    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur introuvable
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Décoder le token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Chercher l'utilisateur
    user = await User.find_one(User.username == username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifie que l'utilisateur est actif.

    Args:
        current_user: Utilisateur depuis get_current_user

    Returns:
        User: Utilisateur actif

    Raises:
        HTTPException: Si l'utilisateur est inactif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# async def get_optional_current_user(
#         token: Optional[str] = Depends(oauth2_scheme)
# ) -> Optional[User]:
#     """
#     Récupère l'utilisateur si un token est fourni.
#     Ne lève pas d'exception si pas de token.
#
#     Args:
#         token: Token JWT optionnel
#
#     Returns:
#         Optional[User]: Utilisateur si authentifié, None sinon
#     """
#     if not token:
#         return None
#
#     try:
#         return await get_current_user(token)
#     except HTTPException:
#         return None

security = HTTPBearer(auto_error=False)  # auto_error=False pour ne pas lever 401 automatiquement

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    if credentials is None:
        return None
    token = credentials.credentials
    try:
        return await get_current_user(token)
    except HTTPException:
        return None