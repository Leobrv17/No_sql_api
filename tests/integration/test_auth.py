"""
Tests d'intégration pour l'authentification.
Teste les endpoints de registration et login.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """
    Teste l'inscription réussie d'un nouvel utilisateur.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 200
        - Utilisateur créé avec les bonnes données
        - Pas de mot de passe dans la réponse
    """
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepassword123",
        "full_name": "New User"
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert response.status_code == 200
    data = response.json()

    # Vérifier les données retournées
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data
    assert "hashed_password" not in data
    assert "_id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """
    Teste l'inscription avec un email déjà utilisé.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur existant

    Expected:
        - Status 409 (Conflict)
        - Message d'erreur approprié
    """
    user_data = {
        "email": test_user.email,  # Email déjà pris
        "username": "anotheruser",
        "password": "password123"
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_data(client: AsyncClient):
    """
    Teste l'inscription avec des données invalides.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 422 (Validation Error)
        - Détails sur les erreurs de validation
    """
    # Email invalide et mot de passe trop court
    user_data = {
        "email": "not-an-email",
        "username": "user",
        "password": "short"
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) > 0


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """
    Teste la connexion réussie avec username.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test

    Expected:
        - Status 200
        - Token JWT valide retourné
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_with_email(client: AsyncClient, test_user):
    """
    Teste la connexion avec email au lieu du username.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test

    Expected:
        - Status 200
        - Connexion acceptée avec email
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,  # Email comme username
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """
    Teste la connexion avec un mauvais mot de passe.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test

    Expected:
        - Status 401 (Unauthorized)
        - Message d'erreur approprié
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """
    Teste la connexion avec un utilisateur inexistant.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 401 (Unauthorized)
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )

    assert response.status_code == 401