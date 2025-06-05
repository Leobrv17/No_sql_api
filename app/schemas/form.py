"""
Schémas Pydantic pour les formulaires.
Définit les formats d'entrée/sortie de l'API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class FormBase(BaseModel):
    """Attributs communs des formulaires."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True
    accepts_responses: bool = True
    requires_auth: bool = False


class FormCreate(FormBase):
    """Schéma pour créer un formulaire."""
    pass


class FormUpdate(BaseModel):
    """Schéma pour mettre à jour un formulaire."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    accepts_responses: Optional[bool] = None
    requires_auth: Optional[bool] = None


class FormResponse(FormBase):
    """Schéma de réponse pour un formulaire."""
    id: str = Field(..., alias="_id")
    owner_id: str
    response_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class FormWithQuestions(FormResponse):
    """Formulaire avec ses questions."""
    questions: List["QuestionResponse"] = []


# Import circulaire résolu
from app.schemas.question import QuestionResponse

FormWithQuestions.model_rebuild()