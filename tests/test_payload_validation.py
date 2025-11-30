import pytest
from flask import Flask

from src.infrastructure.flask.auth import AuthService, ScopeAuthorizer
from src.infrastructure.flask.routes import build_blueprint
from src.interface_adapters.gateways.in_memory_plant_repository import (
    InMemoryPlantRepository,
)
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.get_system import GetSystemUseCase


class DummyUnitOfWork:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def commit(self):  # pragma: no cover - no-op en memoria
        return None

    def rollback(self):  # pragma: no cover - no-op en memoria
        return None

    @property
    def session(self):  # pragma: no cover - no session para repos en memoria
        return None


@pytest.fixture()
def auth_service():
    return AuthService(secret_key="validation-secret", token_ttl_seconds=3600)


@pytest.fixture()
def flask_app(auth_service: AuthService) -> Flask:
    repository = InMemoryPlantRepository()
    scope = ScopeAuthorizer(
        get_area=GetAreaUseCase(repository).execute,
        get_equipment=GetEquipmentUseCase(repository).execute,
        get_system=GetSystemUseCase(repository).execute,
    )

    app = Flask(__name__)
    app.register_blueprint(
        build_blueprint(
            repository,
            DummyUnitOfWork,
            auth_service=auth_service,
            scope_authorizer=scope,
        )
    )
    app.testing = True
    return app


@pytest.fixture()
def client(flask_app: Flask):
    return flask_app.test_client()


@pytest.fixture()
def superadmin_headers(auth_service: AuthService) -> dict[str, str]:
    token = auth_service.issue_token("superadmin", "superadmin")
    return {"Authorization": f"Bearer {token}"}


def test_create_plant_requires_nombre(client, superadmin_headers):
    response = client.post("/api/plantas", headers=superadmin_headers, json={})

    assert response.status_code == 400
    assert response.get_json() == {"message": "El campo 'nombre' es obligatorio"}


def test_update_plant_requires_nombre(client, superadmin_headers):
    response = client.put("/api/plantas/1", headers=superadmin_headers, json={})

    assert response.status_code == 400
    assert response.get_json() == {"message": "El campo 'nombre' es obligatorio"}


def test_create_area_requires_nombre(client, superadmin_headers):
    response = client.post(
        "/api/plantas/1/areas", headers=superadmin_headers, json={"nombre": ""}
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "El campo 'nombre' es obligatorio"}


def test_update_equipment_requires_nombre(client, superadmin_headers):
    response = client.put(
        "/api/equipos/1001", headers=superadmin_headers, json={"nombre": None}
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "El campo 'nombre' es obligatorio"}
