"""
Schémas Pydantic pour les utilisateurs.
Définit les formats d'entrée/sortie de l'API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Attributs communs des utilisateurs."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schéma de réponse pour un utilisateur."""
    id: str = Field(..., alias="_id")
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class UserLogin(BaseModel):
    """Schéma pour la connexion."""
    username: str  # Peut être email ou username
    password: str


class Token(BaseModel):
    """Schéma pour le token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Données contenues dans le token JWT."""
    username: Optional[str] = None