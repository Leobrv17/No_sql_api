"""
Utilitaires de sécurité pour l'authentification et l'autorisation.
Gère le hashing des mots de passe et les tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

# Contexte pour le hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash.

    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash bcrypt du mot de passe

    Returns:
        bool: True si le mot de passe est correct
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt.

    Args:
        password: Mot de passe en clair

    Returns:
        str: Hash bcrypt du mot de passe
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT avec les données fournies.

    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token

    Returns:
        str: Token JWT encodé
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode et valide un token JWT.

    Args:
        token: Token JWT à décoder

    Returns:
        dict: Données du token si valide, None sinon
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None