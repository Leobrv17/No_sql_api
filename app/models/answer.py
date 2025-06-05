"""
Modèles Answer et FormResponse pour Beanie ODM.
Stockent les réponses aux formulaires.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from beanie import Document, Link
from pydantic import Field, validator
from app.models.form import Form
from app.models.question import Question
from app.models.user import User


class Answer(Document):
    """
    Document MongoDB pour une réponse individuelle à une question.
    Supporte différents types de valeurs selon le type de question.
    """
    question: Link[Question]  # Question concernée
    form_response: Optional[str] = None  # ID de FormResponse

    # Valeur de la réponse (polymorphe selon le type)
    value: Union[str, List[str], int, float, datetime, None] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "answers"
        indexes = [
            [("question", 1), ("form_response", 1)]
        ]


class FormResponse(Document):
    """
    Document MongoDB regroupant toutes les réponses d'un utilisateur
    pour un formulaire donné.
    """
    form: Link[Form]  # Formulaire concerné
    respondent: Optional[Link[User]] = None  # Null si anonyme

    # Métadonnées de soumission
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Statut
    is_complete: bool = True
    is_valid: bool = True

    class Settings:
        name = "form_responses"
        indexes = [
            [("form", 1), ("submitted_at", -1)],
            [("respondent", 1), ("form", 1)]
        ]