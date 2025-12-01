"""
Path: src/infrastructure/flask/app.py
"""

from flask import Flask, request, redirect
from werkzeug.exceptions import HTTPException

from src.infrastructure.flask.auth import AuthService, mask_authorization_header
from src.infrastructure.flask.routes import build_blueprint
from src.infrastructure.flask.error_handlers import (
    handle_http_exception,
    handle_unexpected_exception,
)
from src.infrastructure.sqlalchemy import (
    SqlAlchemyPlantRepository,
    SqlAlchemyUnitOfWork,
    SqlAlchemyUserRepository,
)
from src.infrastructure.sqlalchemy.config import load_db_config
from src.infrastructure.sqlalchemy.session import (
    SessionFactory,
    build_session_factory,
    create_engine_from_config,
)
from src.shared.config import get_cors_origins, get_env
from src.shared.logger import get_logger

logger = get_logger("flask-app")


def create_app() -> Flask:
    "Bootstrap Flask application with shared repository and routes."
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
    session_factory: SessionFactory = build_session_factory(engine)
    repository = SqlAlchemyPlantRepository(session_factory)
    user_repository = SqlAlchemyUserRepository(session_factory)

    def make_uow() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    uow_factory = make_uow

    auth_service = AuthService(user_repository=user_repository)

    flask_app.register_blueprint(
        build_blueprint(repository, uow_factory, auth_service=auth_service)
    )
    flask_app.register_error_handler(HTTPException, handle_http_exception)
    flask_app.register_error_handler(Exception, handle_unexpected_exception)

    @flask_app.before_request
    def log_request_context():
        if request.method == "OPTIONS":
            return

        auth_header = request.headers.get("Authorization")
        if auth_header:
            logger.debug(
                "Petición %s %s con Authorization %s",
                request.method,
                request.path,
                mask_authorization_header(auth_header),
            )
        else:
            logger.debug(
                "Petición %s %s sin Authorization. Headers recibidos: %s",
                request.method,
                request.path,
                sorted(request.headers.keys()),
            )

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
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"

        if request.method == "OPTIONS":
            response.status_code = 200

        return response

    @flask_app.route("/api/health", methods=["GET"])
    def health_check() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @flask_app.route("/api/cors", methods=["GET"])
    def cors_info():
        return {"cors_origins": cors_origins}, 200

    @flask_app.route("/", methods=["GET"])
    def forward_to_web():
        web_url = get_env("WEB_URL")
        return redirect(web_url, code=302)

    return flask_app


app = create_app()
