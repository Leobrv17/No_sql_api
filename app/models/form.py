"""
Modèle Form pour Beanie ODM.
Représente un formulaire créé par un utilisateur.
"""

from datetime import datetime
from typing import Optional, List
from beanie import Document, Link, Indexed
from pydantic import Field
from app.models.user import User


class Form(Document):
    """
    Document MongoDB pour stocker les formulaires.
    Chaque formulaire appartient à un utilisateur créateur.
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    owner: Link[User]  # Référence au créateur du formulaire
    is_active: bool = True  # Formulaire actif ou archivé
    accepts_responses: bool = True  # Accepte de nouvelles réponses
    requires_auth: bool = False  # Réponses anonymes autorisées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Statistiques
    response_count: int = 0

    class Settings:
        name = "forms"
        indexes = [
            [("owner", 1), ("created_at", -1)]  # Index composé
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Enquête de satisfaction",
                "description": "Merci de prendre quelques minutes...",
                "is_active": True,
                "accepts_responses": True,
                "requires_auth": False
            }
        }