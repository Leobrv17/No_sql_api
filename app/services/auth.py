"""
Service d'authentification.
Gère la connexion et l'inscription des utilisateurs.
"""

from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import verify_password, get_password_hash
from app.exceptions.http import (
    UnauthorizedException,
    ConflictException
)


async def authenticate_user(
        username: str,
        password: str
) -> Optional[User]:
    """
    Authentifie un utilisateur avec username/email et mot de passe.

    Args:
        username: Username ou email de l'utilisateur
        password: Mot de passe en clair

    Returns:
        User: Utilisateur si authentification réussie, None sinon
    """
    # Chercher par username ou email
    user = await User.find_one({
        "$or": [
            {"username": username},
            {"email": username}
        ]
    })

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def create_user(user_data: UserCreate) -> User:
    """
    Crée un nouvel utilisateur avec validation.

    Args:
        user_data: Données du nouvel utilisateur

    Returns:
        User: Utilisateur créé

    Raises:
        ConflictException: Si username ou email déjà pris
    """
    # Vérifier l'unicité de l'email
    existing_email = await User.find_one(
        User.email == user_data.email
    )
    if existing_email:
        raise ConflictException("Email already registered")

    # Vérifier l'unicité du username
    existing_username = await User.find_one(
        User.username == user_data.username
    )
    if existing_username:
        raise ConflictException("Username already taken")

    # Créer l'utilisateur
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=user_data.is_active
    )

    await user.save()
    return user