"""Bootstrap de la aplicación Flask con inyección de dependencias."""

from flask import Flask

from src.infrastructure.db.config import load_db_config
from src.infrastructure.db.session import build_session_factory, create_engine_from_config
from src.infrastructure.db.sqlalchemy_plant_repository import SqlAlchemyPlantRepository
from src.interface_adapters.controllers.flask_routes import build_blueprint


def create_app() -> Flask:
    """Configura Flask, el repositorio y registra los blueprints."""

    flask_app = Flask(__name__)

    config = load_db_config()
    engine = create_engine_from_config(config)
    session_factory = build_session_factory(engine)
    repository = SqlAlchemyPlantRepository(session_factory)

    flask_app.register_blueprint(build_blueprint(repository))

    @flask_app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return flask_app


app = create_app()
