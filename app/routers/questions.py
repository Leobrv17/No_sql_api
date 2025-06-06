"""
Router pour la gestion des questions.
Expose les endpoints CRUD pour les questions.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse
)
from app.services.question import (
    create_question,
    update_question,
    delete_question,
    reorder_questions
)
from app.services.form import get_form_by_id
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/forms/{form_id}/questions", tags=["Questions"])


@router.post("/", response_model=QuestionResponse)
async def create_new_question(
    form_id: str,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crée une nouvelle question dans un formulaire.

    Args:
        form_id: ID du formulaire
        question_data: Données de la question
        current_user: Utilisateur authentifié

    Returns:
        QuestionResponse: Question créée
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    question = await create_question(form_id, question_data)

    return QuestionResponse(
        _id=str(question.id),
        form_id=str(question.form.id),
        title=question.title,
        description=question.description,
        question_type=question.question_type,
        is_required=question.is_required,
        order=question.order,
        options=question.options,
        min_length=question.min_length,
        max_length=question.max_length,
        min_value=question.min_value,
        max_value=question.max_value,
        created_at=question.created_at,
        updated_at=question.updated_at
    )


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_existing_question(
    form_id: str,
    question_id: str,
    question_update: QuestionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Met à jour une question existante.

    Args:
        form_id: ID du formulaire
        question_id: ID de la question
        question_update: Données à mettre à jour
        current_user: Utilisateur authentifié

    Returns:
        QuestionResponse: Question mise à jour
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    question = await update_question(question_id, question_update)
    await question.fetch_link("form")
    return QuestionResponse(
        _id=str(question.id),
        form_id=str(question.form.id),
        title=question.title,
        description=question.description,
        question_type=question.question_type,
        is_required=question.is_required,
        order=question.order,
        options=question.options,
        min_length=question.min_length,
        max_length=question.max_length,
        min_value=question.min_value,
        max_value=question.max_value,
        created_at=question.created_at,
        updated_at=question.updated_at
    )


@router.delete("/{question_id}")
async def delete_existing_question(
    form_id: str,
    question_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Supprime une question.

    Args:
        form_id: ID du formulaire
        question_id: ID de la question
        current_user: Utilisateur authentifié

    Returns:
        dict: Message de confirmation
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    await delete_question(question_id)
    return {"message": "Question deleted successfully"}


@router.post("/reorder")
async def reorder_form_questions(
    form_id: str,
    question_orders: List[dict],
    current_user: User = Depends(get_current_active_user)
):
    """
    Réordonne les questions d'un formulaire.

    Args:
        form_id: ID du formulaire
        question_orders: Liste de {question_id, order}
        current_user: Utilisateur authentifié

    Returns:
        dict: Message de confirmation
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    await reorder_questions(form_id, question_orders)
    return {"message": "Questions reordered successfully"}