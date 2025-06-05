"""
Modèle User pour Beanie ODM.
Représente un utilisateur dans la base de données.
"""

from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    """
    Document MongoDB pour stocker les informations utilisateur.
    Utilise Beanie pour la gestion ODM.
    """
    email: Indexed(EmailStr, unique=True)  # Email unique et indexé
    username: Indexed(str, unique=True)  # Username unique et indexé
    hashed_password: str  # Mot de passe hashé avec bcrypt
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # Nom de la collection MongoDB

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False
            }
        }