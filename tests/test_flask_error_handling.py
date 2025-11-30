from flask import Flask
from werkzeug.exceptions import HTTPException

from src.infrastructure.flask.routes import build_blueprint
from src.infrastructure.flask.auth import AuthService, ScopeAuthorizer
from src.infrastructure.flask.error_handlers import (
    handle_http_exception,
    handle_unexpected_exception,
)
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.get_system import GetSystemUseCase


class DummyUnitOfWork:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @property
    def session(self):
        return None

    def commit(self):
        pass

    def rollback(self):
        pass


class BaseRepository:
    def list_plants(self, *, session=None):
        return []

    def get_plant(self, plant_id, *, session=None):
        return None

    def create_plant(self, *, name, location=None, status=None, session=None):
        raise NotImplementedError

    def update_plant(
        self, plant_id, *, name=None, location=None, status=None, session=None
    ):
        raise NotImplementedError

    def delete_plant(self, plant_id, *, session=None):
        raise NotImplementedError

    def list_areas(self, plant_id, *, session=None):
        raise NotImplementedError

    def get_area(self, area_id, *, session=None):
        raise NotImplementedError

    def create_area(self, plant_id, *, name, status=None, session=None):
        raise NotImplementedError

    def update_area(self, area_id, *, name=None, status=None, session=None):
        raise NotImplementedError

    def delete_area(self, area_id, *, session=None):
        raise NotImplementedError

    def list_equipment(self, area_id, *, session=None):
        raise NotImplementedError

    def get_equipment(self, equipment_id, *, session=None):
        raise NotImplementedError

    def create_equipment(self, area_id, *, name, status=None, session=None):
        raise NotImplementedError

    def update_equipment(self, equipment_id, *, name=None, status=None, session=None):
        raise NotImplementedError

    def delete_equipment(self, equipment_id, *, session=None):
        raise NotImplementedError

    def list_systems(self, equipment_id, *, session=None):
        raise NotImplementedError

    def get_system(self, system_id, *, session=None):
        raise NotImplementedError

    def create_system(self, equipment_id, *, name, status=None, session=None):
        raise NotImplementedError

    def update_system(self, system_id, *, name=None, status=None, session=None):
        raise NotImplementedError

    def delete_system(self, system_id, *, session=None):
        raise NotImplementedError


class ErroringRepository(BaseRepository):
    def list_plants(self, *, session=None):
        raise RuntimeError("boom")


class OKRepository(BaseRepository):
    pass


def build_app(repository):
    auth_service = AuthService(secret_key="tests-secret")
    scope = ScopeAuthorizer(
        get_area=GetAreaUseCase(repository).execute,
        get_equipment=GetEquipmentUseCase(repository).execute,
        get_system=GetSystemUseCase(repository).execute,
    )

    app = Flask(__name__)
    app.register_blueprint(
        build_blueprint(
            repository,
            lambda: DummyUnitOfWork(),
            auth_service=auth_service,
            scope_authorizer=scope,
        )
    )
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_unexpected_exception)
    app.config["auth_service"] = auth_service
    return app


def test_method_not_allowed_returns_json_message():
    app = build_app(OKRepository())
    client = app.test_client()
    headers = {
        "Authorization": f"Bearer {app.config['auth_service'].issue_token('superadmin', 'superadmin')}"
    }

    response = client.patch("/api/plantas", headers=headers)

    assert response.status_code == 405
    assert response.get_json() == {
        "message": "The method is not allowed for the requested URL."
    }


def test_unexpected_error_returns_internal_server_error_message():
    app = build_app(ErroringRepository())
    client = app.test_client()
    headers = {
        "Authorization": f"Bearer {app.config['auth_service'].issue_token('superadmin', 'superadmin')}"
    }

    response = client.get("/api/plantas", headers=headers)

    assert response.status_code == 500
    assert response.get_json() == {"message": "Internal server error"}
