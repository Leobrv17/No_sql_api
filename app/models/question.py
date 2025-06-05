"""
Modèle Question pour Beanie ODM.
Représente une question appartenant à un formulaire.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from beanie import Document, Link
from pydantic import Field, validator
from app.models.form import Form


class QuestionType(str, Enum):
    """Types de questions supportés."""
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"


class Question(Document):
    """
    Document MongoDB pour stocker les questions d'un formulaire.
    Supporte différents types de questions avec validation.
    """
    form: Link[Form]  # Référence au formulaire parent
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    question_type: QuestionType
    is_required: bool = False
    order: int = Field(0, ge=0)  # Ordre d'affichage

    # Options pour les questions à choix
    options: Optional[List[str]] = None

    # Contraintes pour les réponses
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('options')
    def validate_options(cls, v, values):
        """
        Valide que les options sont fournies pour les types qui en nécessitent.

        Args:
            v: Valeur des options
            values: Autres valeurs du modèle

        Returns:
            List[str]: Options validées
        """
        if 'question_type' in values:
            needs_options = [
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.CHECKBOX,
                QuestionType.DROPDOWN
            ]
            if values['question_type'] in needs_options and not v:
                raise ValueError(f"{values['question_type']} requires options")
        return v

    class Settings:
        name = "questions"
        indexes = [
            [("form", 1), ("order", 1)]  # Index pour tri
        ]