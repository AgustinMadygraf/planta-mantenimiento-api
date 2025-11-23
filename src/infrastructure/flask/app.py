from flask import Flask

from src.infrastructure.db.config import load_db_config
from src.infrastructure.db.session import build_session_factory, create_engine_from_config
from src.infrastructure.db.sqlalchemy_plant_repository import SqlAlchemyPlantRepository
from src.interface_adapters.controllers.flask_routes import build_blueprint
from src.shared.logger_fastapi import get_logger

logger = get_logger("flask-app")


def create_app() -> Flask:
    """Bootstrap Flask application with shared repository and routes."""

    flask_app = Flask(__name__)

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

    @flask_app.route("/api/health", methods=["GET"])  # simple health check
    def health_check() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    return flask_app


app = create_app()
