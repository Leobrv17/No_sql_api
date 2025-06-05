"""
Router pour l'authentification.
Gère les endpoints de connexion et inscription.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import authenticate_user, create_user
from app.utils.security import create_access_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """
    Inscrit un nouvel utilisateur.

    Args:
        user_data: Données du nouvel utilisateur

    Returns:
        UserResponse: Utilisateur créé
    """
    user = await create_user(user_data)
    return UserResponse(
        _id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Connecte un utilisateur et retourne un token JWT.

    Args:
        form_data: Username/email et mot de passe

    Returns:
        Token: Token d'accès JWT

    Raises:
        HTTPException: Si authentification échouée
    """
    user = await authenticate_user(
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer le token
    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token)