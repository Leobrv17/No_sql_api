"""
Point d'entrée principal de l'application FastAPI.
Configure l'application, les middlewares et les routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, forms, questions, answers

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    Connecte à MongoDB au démarrage et ferme à l'arrêt.
    """
    # Démarrage
    logger.info("Starting up Forms API...")
    await connect_to_mongo()
    yield
    # Arrêt
    logger.info("Shutting down Forms API...")
    await close_mongo_connection()


# Créer l'application FastAPI
def create_app() -> FastAPI:
    """
    Factory pour créer l'application FastAPI.

    Returns:
        FastAPI: Application configurée
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Configurer CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    

    # Inclure les routers
    app.include_router(
        auth.router,
        prefix="/api/v1"
    )
    app.include_router(
        forms.router,
        prefix="/api/v1"
    )
    app.include_router(
        questions.router,
        prefix="/api/v1"
    )
    app.include_router(
        answers.router,
        prefix="/api/v1"
    )

    # Route de santé
    @app.get("/health")
    async def health_check():
        """Vérifie que l'API est opérationnelle."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version
        }

    return app


# Instance de l'application
app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )