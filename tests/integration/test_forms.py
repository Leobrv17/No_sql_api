"""
Tests d'intégration pour la gestion des formulaires.
Teste les opérations CRUD sur les formulaires.
"""

import pytest
from httpx import AsyncClient
from app.models import User, Form


@pytest.mark.asyncio
async def test_create_form_success(
        client: AsyncClient,
        auth_headers: dict
):
    """
    Teste la création réussie d'un formulaire.

    Args:
        client: Client HTTP de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Formulaire créé avec les bonnes données
        - ID et timestamps présents
    """
    form_data = {
        "title": "Test Survey",
        "description": "A test survey description",
        "accepts_responses": True
    }

    response = await client.post(
        "/api/v1/forms/",
        json=form_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == form_data["title"]
    assert data["description"] == form_data["description"]
    assert data["accepts_responses"] is True
    assert "_id" in data
    assert "created_at" in data
    assert data["response_count"] == 0


@pytest.mark.asyncio
async def test_create_form_unauthorized(client: AsyncClient):
    """
    Teste la création de formulaire sans authentification.

    Args:
        client: Client HTTP de test

    Expected:
        - Status 401 (Unauthorized)
    """
    form_data = {"title": "Test"}

    response = await client.post(
        "/api/v1/forms/",
        json=form_data
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_user_forms(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la liste des formulaires d'un utilisateur.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Liste des formulaires de l'utilisateur uniquement
        - Tri par date décroissante
    """
    # Créer quelques formulaires
    for i in range(3):
        form = Form(
            title=f"Form {i}",
            owner=test_user,
            response_count=i
        )
        await form.save()

    response = await client.get(
        "/api/v1/forms/",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    # Vérifier le tri (plus récent en premier)
    assert data[0]["title"] == "Form 2"
    assert all(f["owner_id"] == str(test_user.id) for f in data)


@pytest.mark.asyncio
async def test_get_form_details(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la récupération des détails d'un formulaire.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Détails complets avec questions
    """
    # Créer un formulaire
    form = Form(
        title="Detailed Form",
        description="With questions",
        owner=test_user
    )
    await form.save()

    response = await client.get(
        f"/api/v1/forms/{form.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Detailed Form"
    assert "questions" in data
    assert isinstance(data["questions"], list)


@pytest.mark.asyncio
async def test_update_form(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la mise à jour d'un formulaire.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Formulaire mis à jour correctement
        - updated_at modifié
    """
    # Créer un formulaire
    form = Form(
        title="Original Title",
        owner=test_user
    )
    await form.save()
    original_updated = form.updated_at

    update_data = {
        "title": "Updated Title",
        "accepts_responses": False
    }

    response = await client.patch(
        f"/api/v1/forms/{form.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Title"
    assert data["accepts_responses"] is False
    assert data["updated_at"] != str(original_updated)


@pytest.mark.asyncio
async def test_delete_form(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la suppression d'un formulaire.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Formulaire supprimé de la base
    """
    # Créer un formulaire
    form = Form(title="To Delete", owner=test_user)
    await form.save()

    response = await client.delete(
        f"/api/v1/forms/{form.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    # Vérifier que le formulaire n'existe plus
    deleted_form = await Form.get(form.id)
    assert deleted_form is None


@pytest.mark.asyncio
async def test_access_other_user_form(
        client: AsyncClient,
        auth_headers: dict
):
    """
    Teste l'accès à un formulaire d'un autre utilisateur.

    Args:
        client: Client HTTP de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 403 (Forbidden)
    """
    # Créer un autre utilisateur et son formulaire
    from app.utils.security import get_password_hash

    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password=get_password_hash("password")
    )
    await other_user.save()

    form = Form(title="Other's Form", owner=other_user)
    await form.save()

    # Essayer d'y accéder avec notre token
    response = await client.get(
        f"/api/v1/forms/{form.id}",
        headers=auth_headers
    )

    assert response.status_code == 403