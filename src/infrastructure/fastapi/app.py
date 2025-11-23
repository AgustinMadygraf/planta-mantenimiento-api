from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interface_adapters.controllers.areas import router as areas_router
from src.interface_adapters.controllers.equipment import router as equipment_router
from src.interface_adapters.controllers.plants import router as plants_router
from src.interface_adapters.controllers.systems import router as systems_router


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

    fastapi_app.include_router(plants_router)
    fastapi_app.include_router(areas_router)
    fastapi_app.include_router(equipment_router)
    fastapi_app.include_router(systems_router)

    @fastapi_app.get("/api/health", summary="Verifica que la API esté disponible")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return fastapi_app


app = create_app()
