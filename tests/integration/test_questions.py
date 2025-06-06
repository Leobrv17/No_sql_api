"""
Tests d'intégration pour la gestion des questions.
Teste la création et modification des questions.
"""

import pytest
from httpx import AsyncClient
from app.models import User, Form, Question, QuestionType


async def create_test_form(user: User) -> Form:
    """
    Helper pour créer un formulaire de test.

    Args:
        user: Propriétaire du formulaire

    Returns:
        Form: Formulaire créé
    """
    form = Form(
        title="Test Form for Questions",
        owner=user
    )
    await form.save()
    return form


@pytest.mark.asyncio
async def test_create_text_question(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la création d'une question texte.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Question créée avec bon type
    """
    form = await create_test_form(test_user)

    question_data = {
        "title": "What is your name?",
        "question_type": "short_text",
        "is_required": True,
        "order": 1
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == question_data["title"]
    assert data["question_type"] == "short_text"
    assert data["is_required"] is True
    assert data["form_id"] == str(form.id)


@pytest.mark.asyncio
async def test_create_multiple_choice_question(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la création d'une question à choix multiple.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Options correctement enregistrées
    """
    form = await create_test_form(test_user)

    question_data = {
        "title": "Choose your favorite color",
        "question_type": "multiple_choice",
        "options": ["Red", "Blue", "Green", "Yellow"],
        "is_required": False,
        "order": 2
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["question_type"] == "multiple_choice"
    assert data["options"] == question_data["options"]
    assert len(data["options"]) == 4


@pytest.mark.asyncio
async def test_create_question_missing_options(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la validation des options manquantes.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 422 (Validation Error)
        - Erreur pour options manquantes
    """
    form = await create_test_form(test_user)

    question_data = {
        "title": "Choose one",
        "question_type": "multiple_choice",
        # options manquantes
        "is_required": True
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_number_question_with_constraints(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la création d'une question nombre avec contraintes.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Contraintes min/max enregistrées
    """
    form = await create_test_form(test_user)

    question_data = {
        "title": "Enter your age",
        "question_type": "number",
        "is_required": True,
        "min_value": 18,
        "max_value": 100,
        "order": 3
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["question_type"] == "number"
    assert data["min_value"] == 18
    assert data["max_value"] == 100


@pytest.mark.asyncio
async def test_create_checkbox_question(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la création d'une question checkbox (choix multiples).

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Type checkbox avec options
    """
    form = await create_test_form(test_user)

    question_data = {
        "title": "Select all that apply",
        "question_type": "checkbox",
        "options": ["Option A", "Option B", "Option C"],
        "is_required": False,
        "order": 4
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["question_type"] == "checkbox"
    assert len(data["options"]) == 3


@pytest.mark.asyncio
async def test_update_question(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la mise à jour d'une question.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Question mise à jour
    """
    form = await create_test_form(test_user)

    # Créer une question
    question = Question(
        form=form,
        title="Original Title",
        question_type=QuestionType.SHORT_TEXT,
        order=1
    )
    await question.save()

    update_data = {
        "title": "Updated Title",
        "is_required": True,
        "order": 5
    }

    response = await client.patch(
        f"/api/v1/forms/{form.id}/questions/{question.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Title"
    assert data["is_required"] is True
    assert data["order"] == 5


@pytest.mark.asyncio
async def test_delete_question(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la suppression d'une question.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Question supprimée
    """
    form = await create_test_form(test_user)

    question = Question(
        form=form,
        title="To Delete",
        question_type=QuestionType.SHORT_TEXT
    )
    await question.save()

    response = await client.delete(
        f"/api/v1/forms/{form.id}/questions/{question.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    # Vérifier suppression
    deleted = await Question.get(question.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_reorder_questions(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste le réordonnancement des questions.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Ordre mis à jour
    """
    form = await create_test_form(test_user)

    # Créer 3 questions
    questions = []
    for i in range(3):
        q = Question(
            form=form,
            title=f"Question {i}",
            question_type=QuestionType.SHORT_TEXT,
            order=i
        )
        await q.save()
        questions.append(q)

    # Inverser l'ordre
    reorder_data = [
        {"question_id": str(questions[2].id), "order": 0},
        {"question_id": str(questions[1].id), "order": 1},
        {"question_id": str(questions[0].id), "order": 2}
    ]

    response = await client.post(
        f"/api/v1/forms/{form.id}/questions/reorder",
        json=reorder_data,
        headers=auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_all_question_types(
    client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Teste la création de tous les types de questions.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Tous les types créés avec succès
    """
    form = await create_test_form(test_user)

    question_types = [
        {
            "title": "Short answer",
            "question_type": "short_text",
            "max_length": 100
        },
        {
            "title": "Long answer",
            "question_type": "long_text",
            "max_length": 1000
        },
        {
            "title": "Email address",
            "question_type": "email"
        },
        {
            "title": "Date of birth",
            "question_type": "date"
        },
        {
            "title": "Select from dropdown",
            "question_type": "dropdown",
            "options": ["Option 1", "Option 2"]
        }
    ]

    for i, q_data in enumerate(question_types):
        q_data["order"] = i

        response = await client.post(
            f"/api/v1/forms/{form.id}/questions/",
            json=q_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["question_type"] == q_data["question_type"]


@pytest.mark.asyncio
async def test_question_unauthorized_access(
    client: AsyncClient,
    auth_headers: dict
):
    """
    Teste l'accès non autorisé aux questions.

    Args:
        client: Client HTTP de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 403 pour formulaire d'un autre utilisateur
    """
    # Créer un autre utilisateur et son formulaire
    from app.utils.security import get_password_hash

    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password=get_password_hash("password")
    )
    await other_user.save()

    other_form = Form(
        title="Other User Form",
        owner=other_user
    )
    await other_form.save()

    # Essayer de créer une question
    question_data = {
        "title": "Unauthorized question",
        "question_type": "short_text"
    }

    response = await client.post(
        f"/api/v1/forms/{other_form.id}/questions/",
        json=question_data,
        headers=auth_headers
    )

    assert response.status_code == 403