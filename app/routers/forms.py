"""
Router pour la gestion des formulaires.
Expose les endpoints CRUD pour les formulaires.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from app.models.user import User
from app.schemas.form import (
    FormCreate,
    FormUpdate,
    FormResponse,
    FormWithQuestions
)
from app.schemas.answer import FormStats
from app.services.form import (
    create_form,
    get_user_forms,
    get_form_by_id,
    update_form,
    delete_form,
    get_form_stats
)
from app.services.question import get_form_questions
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/forms", tags=["Forms"])


@router.post("/", response_model=FormResponse)
async def create_new_form(
        form_data: FormCreate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Crée un nouveau formulaire.

    Args:
        form_data: Données du formulaire
        current_user: Utilisateur authentifié

    Returns:
        FormResponse: Formulaire créé
    """
    form = await create_form(form_data, current_user)
    return FormResponse(
        _id=str(form.id),
        **form_data.model_dump(),
        owner_id=str(form.owner.id),
        response_count=form.response_count,
        created_at=form.created_at,
        updated_at=form.updated_at
    )


@router.get("/", response_model=List[FormResponse])
async def list_forms(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: User = Depends(get_current_active_user)
):
    """
    Liste les formulaires de l'utilisateur.

    Args:
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments
        current_user: Utilisateur authentifié

    Returns:
        List[FormResponse]: Liste des formulaires
    """
    forms = await get_user_forms(current_user, skip, limit)
    for form in forms:
        await form.fetch_link("owner")

    return [
        FormResponse(
            _id=str(form.id),
            title=form.title,
            description=form.description,
            is_active=form.is_active,
            accepts_responses=form.accepts_responses,
            requires_auth=form.requires_auth,
            owner_id=str(form.owner.id),  # maintenant que le lien est résolu
            response_count=form.response_count,
            created_at=form.created_at,
            updated_at=form.updated_at
        )
        for form in forms
    ]


@router.get("/{form_id}", response_model=FormWithQuestions)
async def get_form(
        form_id: str,
        current_user: User = Depends(get_current_active_user)
):
    """
    Récupère un formulaire avec ses questions.

    Args:
        form_id: ID du formulaire
        current_user: Utilisateur authentifié

    Returns:
        FormWithQuestions: Formulaire détaillé
    """
    form = await get_form_by_id(form_id, current_user)
    questions = await get_form_questions(form_id)
    await form.fetch_link("owner")

    return FormWithQuestions(
        _id=str(form.id),
        title=form.title,
        description=form.description,
        is_active=form.is_active,
        accepts_responses=form.accepts_responses,
        requires_auth=form.requires_auth,
        owner_id=str(form.owner.id),
        response_count=form.response_count,
        created_at=form.created_at,
        updated_at=form.updated_at,
        questions=questions
    )


@router.patch("/{form_id}", response_model=FormResponse)
async def update_existing_form(
        form_id: str,
        form_update: FormUpdate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Met à jour un formulaire.

    Args:
        form_id: ID du formulaire
        form_update: Données à mettre à jour
        current_user: Utilisateur authentifié

    Returns:
        FormResponse: Formulaire mis à jour
    """
    form = await update_form(form_id, form_update, current_user)
    await form.fetch_link("owner")

    return FormResponse(
        _id=str(form.id),
        title=form.title,
        description=form.description,
        is_active=form.is_active,
        accepts_responses=form.accepts_responses,
        requires_auth=form.requires_auth,
        owner_id=str(form.owner.id),
        response_count=form.response_count,
        created_at=form.created_at,
        updated_at=form.updated_at
    )


@router.delete("/{form_id}")
async def delete_existing_form(
        form_id: str,
        current_user: User = Depends(get_current_active_user)
):
    """
    Supprime un formulaire et ses données.

    Args:
        form_id: ID du formulaire
        current_user: Utilisateur authentifié

    Returns:
        dict: Message de confirmation
    """
    await delete_form(form_id, current_user)
    return {"message": "Form deleted successfully"}


@router.get("/{form_id}/stats", response_model=FormStats)
async def get_form_statistics(
        form_id: str,
        current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les statistiques d'un formulaire.

    Args:
        form_id: ID du formulaire
        current_user: Utilisateur authentifié

    Returns:
        FormStats: Statistiques du formulaire
    """
    # Vérifier les permissions
    await get_form_by_id(form_id, current_user)

    stats = await get_form_stats(form_id)
    return FormStats(**stats)