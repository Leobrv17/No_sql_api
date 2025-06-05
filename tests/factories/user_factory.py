"""
Factory pour créer des utilisateurs de test.
Simplifie la création de données de test cohérentes.
"""

from typing import Optional
from app.models import User
from app.utils.security import get_password_hash


class UserFactory:
    """Factory pour créer des utilisateurs de test."""

    _counter = 0

    @classmethod
    async def create(
            cls,
            email: Optional[str] = None,
            username: Optional[str] = None,
            password: str = "testpassword123",
            full_name: Optional[str] = None,
            is_active: bool = True,
            is_superuser: bool = False
    ) -> User:
        """
        Crée un utilisateur de test avec données par défaut.

        Args:
            email: Email (généré si None)
            username: Username (généré si None)
            password: Mot de passe en clair
            full_name: Nom complet
            is_active: Compte actif
            is_superuser: Super utilisateur

        Returns:
            User: Utilisateur créé et sauvegardé
        """
        cls._counter += 1

        if not email:
            email = f"user{cls._counter}@example.com"
        if not username:
            username = f"user{cls._counter}"
        if not full_name:
            full_name = f"Test User {cls._counter}"

        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            is_superuser=is_superuser
        )

        await user.save()
        return user

    @classmethod
    async def create_batch(cls, count: int) -> list[User]:
        """
        Crée plusieurs utilisateurs.

        Args:
            count: Nombre d'utilisateurs à créer

        Returns:
            list[User]: Liste des utilisateurs créés
        """
        users = []
        for _ in range(count):
            user = await cls.create()
            users.append(user)
        return users