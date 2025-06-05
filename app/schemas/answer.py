"""
Schémas Pydantic pour les réponses.
Définit les formats d'entrée/sortie de l'API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class AnswerBase(BaseModel):
    """Attributs communs des réponses."""
    question_id: str
    value: Union[str, List[str], int, float, datetime, None]


class AnswerCreate(AnswerBase):
    """Schéma pour créer une réponse."""
    pass


class AnswerResponse(AnswerBase):
    """Schéma de réponse pour une réponse."""
    id: str = Field(..., alias="_id")
    form_response_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class FormResponseCreate(BaseModel):
    """Schéma pour soumettre un formulaire complet."""
    answers: List[AnswerCreate]


class FormResponseBase(BaseModel):
    """Attributs communs des soumissions."""
    form_id: str
    is_complete: bool = True
    is_valid: bool = True


class FormResponseDetail(FormResponseBase):
    """Schéma de réponse détaillée."""
    id: str = Field(..., alias="_id")
    respondent_id: Optional[str] = None
    submitted_at: datetime
    answers: List[AnswerResponse] = []

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class FormStats(BaseModel):
    """Statistiques d'un formulaire."""
    total_responses: int
    recent_responses: int  # 7 derniers jours
    completion_rate: float
    average_completion_time: Optional[float] = None