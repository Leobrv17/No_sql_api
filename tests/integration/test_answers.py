"""
Tests d'intégration pour les réponses aux formulaires.
Teste la soumission et consultation des réponses.
"""

import pytest
from httpx import AsyncClient
from app.models import User, Form, Question, QuestionType


async def create_form_with_questions(user: User) -> tuple[Form, list[Question]]:
    """
    Helper pour créer un formulaire avec questions.

    Args:
        user: Propriétaire du formulaire

    Returns:
        tuple: (Form, [Questions])
    """
    form = Form(
        title="Survey Form",
        description="Test survey",
        owner=user,
        accepts_responses=True
    )
    await form.save()

    questions = []

    # Question texte court
    q1 = Question(
        form=form,
        title="Your name?",
        question_type=QuestionType.SHORT_TEXT,
        is_required=True,
        order=0
    )
    await q1.save()
    questions.append(q1)

    # Question choix multiple
    q2 = Question(
        form=form,
        title="Favorite color?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=["Red", "Blue", "Green"],
        is_required=False,
        order=1
    )
    await q2.save()
    questions.append(q2)

    return form, questions


@pytest.mark.asyncio
async def test_submit_anonymous_response(
        client: AsyncClient,
        test_user: User
):
    """
    Teste la soumission anonyme de réponses.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur propriétaire du form

    Expected:
        - Status 200
        - Réponses enregistrées
        - Pas de respondent_id
    """
    form, questions = await create_form_with_questions(test_user)

    response_data = {
        "answers": [
            {
                "question_id": str(questions[0].id),
                "value": "John Doe"
            },
            {
                "question_id": str(questions[1].id),
                "value": "Blue"
            }
        ]
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/submit",
        json=response_data
    )

    assert response.status_code == 200
    data = response.json()

    assert data["form_id"] == str(form.id)
    assert data["respondent_id"] is None
    assert len(data["answers"]) == 2
    assert data["is_valid"] is True


@pytest.mark.asyncio
async def test_submit_authenticated_response(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la soumission authentifiée.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - respondent_id présent
    """
    form, questions = await create_form_with_questions(test_user)

    response_data = {
        "answers": [
            {
                "question_id": str(questions[0].id),
                "value": "Jane Doe"
            }
        ]
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/submit",
        json=response_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["respondent_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_submit_missing_required(
        client: AsyncClient,
        test_user: User
):
    """
    Teste la validation des champs requis.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur propriétaire

    Expected:
        - Status 400
        - Erreur pour champ requis manquant
    """
    form, questions = await create_form_with_questions(test_user)

    # Réponse sans le champ requis
    response_data = {
        "answers": [
            {
                "question_id": str(questions[1].id),
                "value": "Green"
            }
        ]
    }

    response = await client.post(
        f"/api/v1/forms/{form.id}/submit",
        json=response_data
    )

    assert response.status_code == 400
    assert "required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_form_not_accepting(
        client: AsyncClient,
        test_user: User
):
    """
    Teste la soumission à un formulaire fermé.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur propriétaire

    Expected:
        - Status 403
        - Message approprié
    """
    form = Form(
        title="Closed Form",
        owner=test_user,
        accepts_responses=False  # Fermé
    )
    await form.save()

    response = await client.post(
        f"/api/v1/forms/{form.id}/submit",
        json={"answers": []}
    )

    assert response.status_code == 403
    assert "not accepting" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_form_responses(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste la récupération des réponses.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Liste des réponses soumises
    """
    form, questions = await create_form_with_questions(test_user)

    # Soumettre quelques réponses
    for i in range(3):
        response_data = {
            "answers": [{
                "question_id": str(questions[0].id),
                "value": f"User {i}"
            }]
        }
        await client.post(
            f"/api/v1/forms/{form.id}/submit",
            json=response_data
        )

    # Récupérer les réponses
    response = await client.get(
        f"/api/v1/forms/{form.id}/responses",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    # Vérifier l'ordre (plus récent en premier)
    assert data[0]["answers"][0]["value"] == "User 2"


@pytest.mark.asyncio
async def test_get_stats(
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
):
    """
    Teste les statistiques d'un formulaire.

    Args:
        client: Client HTTP de test
        test_user: Utilisateur de test
        auth_headers: Headers d'authentification

    Expected:
        - Status 200
        - Statistiques correctes
    """
    form, questions = await create_form_with_questions(test_user)

    # Soumettre des réponses
    for _ in range(5):
        await client.post(
            f"/api/v1/forms/{form.id}/submit",
            json={
                "answers": [{
                    "question_id": str(questions[0].id),
                    "value": "Test"
                }]
            }
        )

    response = await client.get(
        f"/api/v1/forms/{form.id}/stats",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total_responses"] == 5
    assert "recent_responses" in data
    assert data["completion_rate"] == 1.0