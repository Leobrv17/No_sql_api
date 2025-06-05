"""
Configuration centralisée de l'application.
Charge les variables d'environnement et définit les paramètres globaux.
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Classe de configuration utilisant Pydantic Settings.
    Charge automatiquement les variables depuis .env ou l'environnement.
    """
    # Application
    app_name: str = "Forms API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "forms_db"

    # Security
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne une instance singleton des paramètres.
    Utilise lru_cache pour éviter de recharger à chaque appel.

    Returns:
        Settings: Instance des paramètres de l'application
    """
    return Settings()