from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interface_adapters.controllers.plants import router as plants_router


def create_app() -> FastAPI:
    """Bootstrap the FastAPI application with common middleware and routes."""

    app = FastAPI(title="Gestión de Activos API", version="0.1.0")

    # Permite que el frontend en localhost consuma la API durante el desarrollo.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(plants_router)

    @app.get("/api/health", summary="Verifica que la API esté disponible")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
