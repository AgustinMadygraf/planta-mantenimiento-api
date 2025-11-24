from flask import Flask, request

from src.infrastructure.db.config import load_db_config
from src.infrastructure.db.session import build_session_factory, create_engine_from_config
from src.infrastructure.db.sqlalchemy_plant_repository import SqlAlchemyPlantRepository
from src.interface_adapters.controllers.flask_routes import build_blueprint
from src.shared.config import get_cors_origins
from src.shared.logger_fastapi import get_logger

logger = get_logger("flask-app")


def create_app() -> Flask:
    """Bootstrap Flask application with shared repository and routes."""

    flask_app = Flask(__name__)
    cors_origins = get_cors_origins()

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

    flask_app.register_blueprint(build_blueprint(repository))

    @flask_app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        allow_all = "*" in cors_origins

        if allow_all:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif origin in cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"

        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"

        if request.method == "OPTIONS":
            response.status_code = 200

        return response

    @flask_app.route("/api/health", methods=["GET"])  # simple health check
    def health_check() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    return flask_app


app = create_app()
