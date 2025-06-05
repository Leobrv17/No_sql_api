"""
Service pour la gestion des formulaires.
Contient la logique métier des formulaires.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from app.models.form import Form
from app.models.user import User
from app.models.question import Question
from app.models.answer import FormResponse
from app.schemas.form import FormCreate, FormUpdate
from app.exceptions.http import NotFoundException, ForbiddenException


async def create_form(
        form_data: FormCreate,
        owner: User
) -> Form:
    """
    Crée un nouveau formulaire pour un utilisateur.

    Args:
        form_data: Données du formulaire
        owner: Utilisateur propriétaire

    Returns:
        Form: Formulaire créé
    """
    form = Form(
        **form_data.model_dump(),
        owner=owner
    )
    await form.save()
    return form


async def get_user_forms(
        user: User,
        skip: int = 0,
        limit: int = 100
) -> List[Form]:
    """
    Récupère tous les formulaires d'un utilisateur.

    Args:
        user: Utilisateur propriétaire
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments

    Returns:
        List[Form]: Liste des formulaires
    """
    return await Form.find(
        Form.owner.id == user.id
    ).skip(skip).limit(limit).sort(-Form.created_at).to_list()


async def get_form_by_id(
        form_id: str,
        user: Optional[User] = None
) -> Form:
    """
    Récupère un formulaire par son ID.

    Args:
        form_id: ID du formulaire
        user: Utilisateur pour vérifier les permissions

    Returns:
        Form: Formulaire trouvé

    Raises:
        NotFoundException: Si formulaire introuvable
        ForbiddenException: Si accès non autorisé
    """
    form = await Form.get(form_id)
    if not form:
        raise NotFoundException("Form not found")

    # Vérifier les permissions si user fourni
    if user and form.owner.id != user.id:
        raise ForbiddenException("Access denied")

    return form


async def update_form(
        form_id: str,
        form_update: FormUpdate,
        user: User
) -> Form:
    """
    Met à jour un formulaire.

    Args:
        form_id: ID du formulaire
        form_update: Données à mettre à jour
        user: Utilisateur effectuant la modification

    Returns:
        Form: Formulaire mis à jour
    """
    form = await get_form_by_id(form_id, user)

    # Appliquer les modifications
    update_data = form_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await form.set(update_data)

    return form


async def delete_form(form_id: str, user: User) -> bool:
    """
    Supprime un formulaire et toutes ses données associées.

    Args:
        form_id: ID du formulaire
        user: Utilisateur effectuant la suppression

    Returns:
        bool: True si suppression réussie
    """
    form = await get_form_by_id(form_id, user)

    # Supprimer les questions
    await Question.find(Question.form.id == form.id).delete()

    # Supprimer les réponses
    await FormResponse.find(FormResponse.form.id == form.id).delete()

    # Supprimer le formulaire
    await form.delete()

    return True


async def get_form_stats(form_id: str) -> dict:
    """
    Calcule les statistiques d'un formulaire.

    Args:
        form_id: ID du formulaire

    Returns:
        dict: Statistiques du formulaire
    """
    form = await Form.get(form_id)
    if not form:
        raise NotFoundException("Form not found")

    # Compter les réponses totales
    total_responses = await FormResponse.find(
        FormResponse.form.id == form.id
    ).count()

    # Compter les réponses récentes (7 jours)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_responses = await FormResponse.find(
        FormResponse.form.id == form.id,
        FormResponse.submitted_at >= seven_days_ago
    ).count()

    return {
        "total_responses": total_responses,
        "recent_responses": recent_responses,
        "completion_rate": 1.0,  # À implémenter
        "average_completion_time": None  # À implémenter
    }