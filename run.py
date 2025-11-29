"""Application entrypoint for local development and ad-hoc execution."""

import uvicorn


def main() -> None:
    """Start the FastAPI application with uvicorn."""

    uvicorn.run(
        "src.infrastructure.fastapi.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="certs/key.pem",      # Ruta a tu clave privada
        ssl_certfile="certs/cert.pem",    # Ruta a tu certificado
    )


if __name__ == "__main__":
    main()
