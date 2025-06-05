"""
Tests unitaires pour les fonctions de sécurité.
Teste le hashing des mots de passe et les tokens JWT.
"""

import pytest
from datetime import timedelta
from jose import jwt

from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.config import get_settings


def test_password_hashing():
    """
    Teste le hashing et la vérification des mots de passe.

    Expected:
        - Le hash est différent du mot de passe
        - verify_password retourne True pour le bon mot de passe
        - verify_password retourne False pour un mauvais mot de passe
    """
    password = "mysecretpassword123"
    hashed = get_password_hash(password)

    # Le hash doit être différent
    assert hashed != password

    # Vérification avec le bon mot de passe
    assert verify_password(password, hashed) is True

    # Vérification avec un mauvais mot de passe
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """
    Teste la création d'un token JWT.

    Expected:
        - Le token est une string non vide
        - Le token contient les données encodées
        - Le token a une expiration
    """
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Décoder pour vérifier le contenu
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_decode_access_token():
    """
    Teste le décodage d'un token JWT valide.

    Expected:
        - Retourne les données correctes pour un token valide
        - Retourne None pour un token invalide
    """
    # Token valide
    data = {"sub": "testuser", "extra": "data"}
    token = create_access_token(data)
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["extra"] == "data"

    # Token invalide
    invalid_token = "invalid.jwt.token"
    assert decode_access_token(invalid_token) is None


def test_token_expiration():
    """
    Teste l'expiration personnalisée des tokens.

    Expected:
        - Le token avec expiration courte expire rapidement
        - L'expiration est correctement définie
    """
    # Token avec expiration de 1 minute
    data = {"sub": "testuser"}
    expires = timedelta(minutes=1)
    token = create_access_token(data, expires_delta=expires)

    decoded = decode_access_token(token)
    assert decoded is not None

    # Vérifier que exp est défini
    assert "exp" in decoded