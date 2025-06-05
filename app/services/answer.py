"""
Service pour la gestion des réponses.
Contient la logique métier des soumissions de formulaires.
"""

from typing import List, Optional
from datetime import datetime
from app.models.form import Form
from app.models.question import Question
from app.models.answer import Answer, FormResponse
from app.models.user import User
from app.schemas.answer import FormResponseCreate
from app.exceptions.http import (
    NotFoundException,
    BadRequestException,
    ForbiddenException
)


async def validate_answers(
        form_id: str,
        answers: List[dict]
) -> tuple[bool, List[str]]:
    """
    Valide les réponses par rapport aux questions du formulaire.

    Args:
        form_id: ID du formulaire
        answers: Liste des réponses

    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []

    # Récupérer toutes les questions
    questions = await Question.find(
        Question.form.id == form_id
    ).to_list()

    # Créer un mapping question_id -> question
    question_map = {str(q.id): q for q in questions}
    answer_map = {a["question_id"]: a["value"] for a in answers}

    # Vérifier les questions requises
    for question in questions:
        q_id = str(question.id)

        if question.is_required and (
                q_id not in answer_map or
                answer_map[q_id] is None or
                answer_map[q_id] == ""
        ):
            errors.append(f"Question '{question.title}' is required")

    # Valider chaque réponse
    for answer in answers:
        q_id = answer["question_id"]
        if q_id not in question_map:
            errors.append(f"Invalid question ID: {q_id}")
            continue

        question = question_map[q_id]
        value = answer["value"]

        # Valider selon le type
        if not validate_answer_type(question, value):
            errors.append(
                f"Invalid answer type for '{question.title}'"
            )

    return len(errors) == 0, errors


def validate_answer_type(question: Question, value) -> bool:
    """
    Valide qu'une réponse correspond au type de question.

    Args:
        question: Question
        value: Valeur de la réponse

    Returns:
        bool: True si valide
    """
    if value is None:
        return not question.is_required

    # Mapping des validateurs par type
    validators = {
        "short_text": lambda v: isinstance(v, str),
        "long_text": lambda v: isinstance(v, str),
        "number": lambda v: isinstance(v, (int, float)),
        "email": lambda v: isinstance(v, str) and "@" in v,
        "date": lambda v: isinstance(v, str),  # À améliorer
        "multiple_choice": lambda v: isinstance(v, str),
        "checkbox": lambda v: isinstance(v, list),
        "dropdown": lambda v: isinstance(v, str)
    }

    validator = validators.get(question.question_type.value)
    return validator(value) if validator else True


async def submit_form_response(
        form_id: str,
        response_data: FormResponseCreate,
        respondent: Optional[User] = None,
        metadata: dict = None
) -> FormResponse:
    """
    Enregistre une soumission de formulaire.

    Args:
        form_id: ID du formulaire
        response_data: Données de la soumission
        respondent: Utilisateur répondant (optionnel)
        metadata: Métadonnées (IP, user agent, etc.)

    Returns:
        FormResponse: Soumission enregistrée
    """
    # Vérifier que le formulaire existe et accepte les réponses
    form = await Form.get(form_id)
    if not form:
        raise NotFoundException("Form not found")

    if not form.accepts_responses:
        raise ForbiddenException("Form is not accepting responses")

    if form.requires_auth and not respondent:
        raise ForbiddenException("Authentication required")

    # Valider les réponses
    is_valid, errors = await validate_answers(
        form_id,
        [a.model_dump() for a in response_data.answers]
    )

    if not is_valid:
        raise BadRequestException(f"Invalid answers: {', '.join(errors)}")

    # Créer la soumission
    form_response = FormResponse(
        form=form,
        respondent=respondent,
        is_valid=is_valid,
        ip_address=metadata.get("ip_address") if metadata else None,
        user_agent=metadata.get("user_agent") if metadata else None
    )
    await form_response.save()

    # Créer les réponses individuelles
    for answer_data in response_data.answers:
        question = await Question.get(answer_data.question_id)
        answer = Answer(
            question=question,
            form_response=str(form_response.id),
            value=answer_data.value
        )
        await answer.save()

    # Incrémenter le compteur
    form.response_count += 1
    await form.save()

    return form_response


async def get_form_responses(
        form_id: str,
        skip: int = 0,
        limit: int = 100
) -> List[FormResponse]:
    """
    Récupère toutes les soumissions d'un formulaire.

    Args:
        form_id: ID du formulaire
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments

    Returns:
        List[FormResponse]: Liste des soumissions
    """
    responses = await FormResponse.find(
        FormResponse.form.id == form_id
    ).skip(skip).limit(limit).sort(-FormResponse.submitted_at).to_list()

    return responses


async def get_response_details(
        response_id: str
) -> dict:
    """
    Récupère les détails complets d'une soumission.

    Args:
        response_id: ID de la soumission

    Returns:
        dict: Détails avec les réponses
    """
    response = await FormResponse.get(response_id)
    if not response:
        raise NotFoundException("Response not found")

    # Récupérer toutes les réponses
    answers = await Answer.find(
        Answer.form_response == str(response.id)
    ).to_list()

    return {
        "response": response,
        "answers": answers
    }