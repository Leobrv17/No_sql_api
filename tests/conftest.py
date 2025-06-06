"""
Configuration globale pytest et fixtures partagées.
Configure la base de test et les clients HTTP.
"""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.main import app
from app.config import Settings, get_settings
from app.models import User, Form, Question, Answer, FormResponse


# Override des settings pour les tests
def get_test_settings() -> Settings:
    """
    Retourne les settings modifiés pour les tests.
    Utilise une base de données de test séparée.

    Returns:
        Settings: Configuration pour les tests
    """
    return Settings(
        mongodb_url="mongodb://localhost:27018",
        mongodb_db_name="forms_db_test",
        secret_key="test-secret-key",
        debug=True
    )


# Override la dépendance des settings
app.dependency_overrides[get_settings] = get_test_settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Crée une boucle d'événements pour toute la session de test.
    Nécessaire pour les fixtures async de scope session.

    Yields:
        EventLoop: Boucle d'événements asyncio
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def motor_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """
    Client MongoDB pour les tests.
    Utilise une base de données de test dédiée.

    Yields:
        AsyncIOMotorClient: Client MongoDB
    """
    settings = get_test_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    yield client
    client.close()


@pytest.fixture(scope="function")
async def db(motor_client: AsyncIOMotorClient):
    """
    Initialise la base de données pour chaque test.
    Nettoie la base après chaque test.

    Args:
        motor_client: Client MongoDB

    Yields:
        Database: Base de données de test
    """
    settings = get_test_settings()
    database = motor_client[settings.mongodb_db_name]

    # Initialiser Beanie avec tous les modèles
    await init_beanie(
        database=database,
        document_models=[
            User, Form, Question, Answer, FormResponse
        ]
    )

    yield database

    # Nettoyer toutes les collections après le test
    for collection in await database.list_collection_names():
        await database[collection].delete_many({})


@pytest.fixture
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    """
    Client HTTP asynchrone pour tester l'API.

    Args:
        db: Fixture de base de données

    Yields:
        AsyncClient: Client HTTP configuré
    """
    async with AsyncClient(
            app=app,
            base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(db) -> User:
    """
    Crée un utilisateur de test standard.

    Args:
        db: Base de données de test

    Returns:
        User: Utilisateur créé
    """
    from app.utils.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    await user.save()
    return user


@pytest.fixture
async def auth_headers(test_user: User, client: AsyncClient) -> dict:
    """
    Headers d'authentification avec token JWT valide.

    Args:
        test_user: Utilisateur de test
        client: Client HTTP

    Returns:
        dict: Headers avec Authorization Bearer
    """
    # Se connecter pour obtenir le token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.username,
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}