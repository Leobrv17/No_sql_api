"""
Module de connexion à MongoDB avec Beanie ODM.
Gère l'initialisation et la fermeture de la connexion.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.models.user import User
from app.models.form import Form
from app.models.question import Question
from app.models.answer import Answer, FormResponse
import logging

logger = logging.getLogger(__name__)

# Client MongoDB global
motor_client = None


async def connect_to_mongo():
    """
    Établit la connexion à MongoDB et initialise Beanie.
    Configure tous les modèles de documents.

    Raises:
        Exception: Si la connexion échoue
    """
    global motor_client

    try:
        settings = get_settings()
        motor_client = AsyncIOMotorClient(settings.mongodb_url)

        # Initialiser Beanie avec tous les modèles
        await init_beanie(
            database=motor_client[settings.mongodb_db_name],
            document_models=[
                User,
                Form,
                Question,
                Answer,
                FormResponse
            ]
        )

        logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")

    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Ferme proprement la connexion MongoDB.
    """
    global motor_client

    if motor_client:
        motor_client.close()
        logger.info("Disconnected from MongoDB")