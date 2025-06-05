"""
Tests basiques pour vérifier que l'API est opérationnelle.
Point d'entrée simple pour valider la configuration.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """
    Teste l'endpoint de santé de l'API.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 200
        - Réponse JSON avec status "healthy"
    """
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    """
    Vérifie que la documentation Swagger est accessible.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 200 pour /api/docs
    """
    response = await client.get("/api/docs")
    assert response.status_code == 200