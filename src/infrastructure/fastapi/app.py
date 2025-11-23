from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interface_adapters.controllers.areas import build_router as build_areas_router
from src.interface_adapters.controllers.equipment import build_router as build_equipment_router
from src.interface_adapters.controllers.plants import build_router as build_plants_router
from src.interface_adapters.controllers.systems import build_router as build_systems_router
from src.interface_adapters.gateways.providers import plant_repository


def create_app() -> FastAPI:
    """Bootstrap the FastAPI application with common middleware and routes."""

    fastapi_app = FastAPI(title="Gestión de Activos API", version="0.1.0")

    # Permite que el frontend en localhost consuma la API durante el desarrollo.
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    repository = plant_repository

    fastapi_app.include_router(build_plants_router(repository))
    fastapi_app.include_router(build_areas_router(repository))
    fastapi_app.include_router(build_equipment_router(repository))
    fastapi_app.include_router(build_systems_router(repository))

    @fastapi_app.get("/api/health", summary="Verifica que la API esté disponible")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return fastapi_app


app = create_app()
