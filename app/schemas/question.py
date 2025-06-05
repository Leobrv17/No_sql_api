"""
Schémas Pydantic pour les questions.
Définit les formats d'entrée/sortie de l'API.
"""

from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, validator
from app.models.question import QuestionType


class QuestionBase(BaseModel):
    """Attributs communs des questions."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    question_type: QuestionType
    is_required: bool = False
    order: int = Field(0, ge=0)
    options: Optional[List[str]] = None
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class QuestionCreate(QuestionBase):
    """Schéma pour créer une question."""

    @validator('options')
    def validate_options(cls, v, values):
        """Valide les options selon le type de question."""
        if 'question_type' in values:
            needs_options = [
                QuestionType.MULTIPLE_CHOICE,
                QuestionType.CHECKBOX,
                QuestionType.DROPDOWN
            ]
            if values['question_type'] in needs_options and not v:
                raise ValueError(f"{values['question_type']} requires options")
        return v


class QuestionUpdate(BaseModel):
    """Schéma pour mettre à jour une question."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    is_required: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)
    options: Optional[List[str]] = None
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class QuestionResponse(QuestionBase):
    """Schéma de réponse pour une question."""
    id: str = Field(..., alias="_id")
    form_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )