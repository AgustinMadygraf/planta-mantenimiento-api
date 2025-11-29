"""Punto de entrada para servir la API con Flask."""

from src.infrastructure.flask.app import create_app


def main() -> None:
    "Inicia la aplicación Flask."
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        ssl_context=("certs/cert.pem", "certs/key.pem"),
    )


if __name__ == "__main__":
    main()
