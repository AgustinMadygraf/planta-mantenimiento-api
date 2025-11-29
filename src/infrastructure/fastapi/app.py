from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interface_adapters.controllers.areas import build_router as build_areas_router
from src.interface_adapters.controllers.equipment import build_router as build_equipment_router
from src.interface_adapters.controllers.plants import build_router as build_plants_router
from src.interface_adapters.controllers.systems import build_router as build_systems_router
from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.session import build_session_factory, create_engine_from_config
from src.infrastructure.sqlalchemy.sqlalchemy_plant_repository import SqlAlchemyPlantRepository
from src.shared.config import get_cors_origins
from src.shared.logger_fastapi import get_logger

logger = get_logger("fastapi-app")


def create_app() -> FastAPI:
    """Bootstrap the FastAPI application with common middleware and routes."""

    fastapi_app = FastAPI(title="Gestión de Activos API", version="0.1.0")

    # Permite que el frontend en localhost consuma la API durante el desarrollo.
    cors_origins = get_cors_origins()

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://mantenimiento.profebustos.com.ar"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    try:
        config = load_db_config()
    except RuntimeError as exc:
        logger.error(
            "No se pudo cargar la configuración de base de datos (revisa .env y variables DB_*).",
            exc_info=exc,
        )
        raise

    engine = create_engine_from_config(config)
    session_factory = build_session_factory(engine)
    repository = SqlAlchemyPlantRepository(session_factory)

    fastapi_app.include_router(build_plants_router(repository))
    fastapi_app.include_router(build_areas_router(repository))
    fastapi_app.include_router(build_equipment_router(repository))
    fastapi_app.include_router(build_systems_router(repository))

    @fastapi_app.get("/api/health", summary="Verifica que la API esté disponible")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return fastapi_app


app = create_app()
