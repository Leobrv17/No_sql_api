"""
Service pour la gestion des questions.
Contient la logique métier des questions.
"""

from typing import List
from datetime import datetime
from app.models.question import Question
from app.models.form import Form
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.exceptions.http import NotFoundException


async def create_question(
        form_id: str,
        question_data: QuestionCreate
) -> Question:
    """
    Crée une nouvelle question pour un formulaire.

    Args:
        form_id: ID du formulaire parent
        question_data: Données de la question

    Returns:
        Question: Question créée
    """
    # Vérifier que le formulaire existe
    form = await Form.get(form_id)
    if not form:
        raise NotFoundException("Form not found")

    # Créer la question
    question = Question(
        form=form,
        **question_data.model_dump()
    )
    await question.save()

    return question


async def get_form_questions(form_id: str) -> List[QuestionResponse]:
    """
    Récupère toutes les questions d'un formulaire.

    Args:
        form_id: ID du formulaire

    Returns:
        List[QuestionResponse]: Liste des questions triées
    """
    questions = await Question.find(
        Question.form.id == form_id
    ).sort(Question.order).to_list()

    return [
        QuestionResponse(
            _id=str(q.id),
            form_id=str(q.form.id),
            title=q.title,
            description=q.description,
            question_type=q.question_type,
            is_required=q.is_required,
            order=q.order,
            options=q.options,
            min_length=q.min_length,
            max_length=q.max_length,
            min_value=q.min_value,
            max_value=q.max_value,
            created_at=q.created_at,
            updated_at=q.updated_at
        )
        for q in questions
    ]


async def update_question(
        question_id: str,
        question_update: QuestionUpdate
) -> Question:
    """
    Met à jour une question existante.

    Args:
        question_id: ID de la question
        question_update: Données à mettre à jour

    Returns:
        Question: Question mise à jour
    """
    question = await Question.get(question_id)
    if not question:
        raise NotFoundException("Question not found")

    # Appliquer les modifications
    update_data = question_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await question.set(update_data)

    return question


async def delete_question(question_id: str) -> bool:
    """
    Supprime une question.

    Args:
        question_id: ID de la question

    Returns:
        bool: True si suppression réussie
    """
    question = await Question.get(question_id)
    if not question:
        raise NotFoundException("Question not found")

    await question.delete()
    return True


async def reorder_questions(
        form_id: str,
        question_orders: List[dict]
) -> List[Question]:
    """
    Réordonne les questions d'un formulaire.

    Args:
        form_id: ID du formulaire
        question_orders: Liste de {question_id, order}

    Returns:
        List[Question]: Questions réordonnées
    """
    # Créer un mapping ID -> ordre
    order_map = {item["question_id"]: item["order"]
                 for item in question_orders}

    # Mettre à jour chaque question
    questions = await Question.find(
        Question.form.id == form_id
    ).to_list()

    for question in questions:
        if str(question.id) in order_map:
            question.order = order_map[str(question.id)]
            question.updated_at = datetime.utcnow()
            await question.save()

    return questions