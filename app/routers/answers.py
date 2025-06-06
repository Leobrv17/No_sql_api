"""
Router pour la gestion des réponses.
Expose les endpoints pour soumettre et consulter les réponses.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from app.models.user import User
from app.models.form import Form
from app.schemas.answer import (
    FormResponseCreate,
    FormResponseDetail,
    AnswerResponse
)
from app.services.answer import (
    submit_form_response,
    get_form_responses,
    get_response_details
)
from app.services.form import get_form_by_id
from app.utils.dependencies import (
    get_current_active_user,
    get_optional_current_user
)
from app.exceptions.http import NotFoundException

router = APIRouter(tags=["Answers"])


@router.post("/forms/{form_id}/submit", response_model=FormResponseDetail)
async def submit_form(
        form_id: str,
        response_data: FormResponseCreate,
        request: Request,
        current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Soumet une réponse à un formulaire.

    Args:
        form_id: ID du formulaire
        response_data: Réponses aux questions
        request: Requête HTTP pour les métadonnées
        current_user: Utilisateur optionnel

    Returns:
        FormResponseDetail: Soumission enregistrée
    """
    # Récupérer les métadonnées
    metadata = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", "")
    }

    # Soumettre la réponse
    form_response = await submit_form_response(
        form_id,
        response_data,
        current_user,
        metadata
    )

    # Récupérer les détails
    details = await get_response_details(str(form_response.id))

    return FormResponseDetail(
        _id=str(form_response.id),
        form_id=str(form_response.form),
        respondent_id=str(form_response.respondent.id) if form_response.respondent else None,
        submitted_at=form_response.submitted_at,
        is_complete=form_response.is_complete,
        is_valid=form_response.is_valid,
        answers=[
            AnswerResponse(
                _id=str(a.id),
                question_id=str(a.question),
                value=a.value,
                form_response_id=a.form_response,
                created_at=a.created_at
            )
            for a in details["answers"]
        ]
    )


@router.get("/forms/{form_id}/responses", response_model=List[FormResponseDetail])
async def list_form_responses(
        form_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: User = Depends(get_current_active_user)
):
    """
    Liste les réponses d'un formulaire.

    Args:
        form_id: ID du formulaire
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments
        current_user: Utilisateur authentifié

    Returns:
        List[FormResponseDetail]: Liste des soumissions
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    # Récupérer les réponses
    responses = await get_form_responses(form_id, skip, limit)
    # Construire les détails pour chaque réponse
    result = []
    for response in responses:
        details = await get_response_details(str(response.id))
        result.append(
            FormResponseDetail(
                _id=str(response.id),
                form_id = str(response.form.ref.id),
                respondent_id=str(response.respondent.id) if response.respondent else None,
                submitted_at=response.submitted_at,
                is_complete=response.is_complete,
                is_valid=response.is_valid,
                answers=[
                    AnswerResponse(
                        _id=str(a.id),
                        question_id=str(a.question.ref.id),
                        value=a.value,
                        form_response_id=a.form_response,
                        created_at=a.created_at
                    )
                    for a in details["answers"]
                ]
            )
        )

    return result


@router.get("/responses/{response_id}", response_model=FormResponseDetail)
async def get_single_response(
        response_id: str,
        current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les détails d'une soumission spécifique.

    Args:
        response_id: ID de la soumission
        current_user: Utilisateur authentifié

    Returns:
        FormResponseDetail: Détails de la soumission
    """
    # Récupérer la réponse
    details = await get_response_details(response_id)
    response = details["response"]

    # Vérifier les permissions via le formulaire
    await get_form_by_id(str(response.form.id), current_user)

    return FormResponseDetail(
        _id=str(response.id),
        form_id=str(response.form.id),
        respondent_id=str(response.respondent.id) if response.respondent else None,
        submitted_at=response.submitted_at,
        is_complete=response.is_complete,
        is_valid=response.is_valid,
        answers=[
            AnswerResponse(
                _id=str(a.id),
                question_id=str(a.question.id),
                value=a.value,
                form_response_id=a.form_response,
                created_at=a.created_at
            )
            for a in details["answers"]
        ]
    )