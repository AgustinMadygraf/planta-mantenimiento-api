"""Integración mínima para asegurar que las rutas responden 400 usando Pydantic."""

from __future__ import annotations

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
    """UoW trivial para pruebas que no interactúa con la base."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @property
    def session(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None


@pytest.fixture()
def validation_auth_service() -> AuthService:
    return AuthService(secret_key="validation-secret", token_ttl_seconds=3600)


@pytest.fixture()
def validation_client(validation_auth_service: AuthService):
    repository = InMemoryPlantRepository()
    scope = ScopeAuthorizer(
        get_area=GetAreaUseCase(repository).execute,
        get_equipment=GetEquipmentUseCase(repository).execute,
        get_system=GetSystemUseCase(repository).execute,
    )

    app = Flask("validation")
    app.testing = True
    app.register_blueprint(
        build_blueprint(
            repository,
            DummyUnitOfWork,
            auth_service=validation_auth_service,
            scope_authorizer=scope,
        )
    )
    return app.test_client()


def _auth_headers(auth_service: AuthService) -> dict[str, str]:
    token = auth_service.issue_token("superadmin", "superadmin")
    return {"Authorization": f"Bearer {token}"}


def test_create_plant_requires_nombre(
    validation_client, validation_auth_service: AuthService
):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.post(
        "/api/plantas", headers=headers, json={"estado": "operativa"}
    )

    assert response.status_code == 400
    assert "nombre" in response.get_json()["message"]


def test_create_plant_rejects_long_status(
    validation_client, validation_auth_service: AuthService
):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.post(
        "/api/plantas",
        headers=headers,
        json={"nombre": "Plantita", "estado": "x" * 60},
    )

    assert response.status_code == 400
    assert "estado" in response.get_json()["message"]


def test_update_plant_requires_at_least_one_field(
    validation_client, validation_auth_service: AuthService
):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.put("/api/plantas/1", headers=headers, json={})

    assert response.status_code == 400
    assert "Al menos un campo" in response.get_json()["message"]


def test_login_validation_error(validation_client):
    response = validation_client.post(
        "/api/auth/login", json={"username": "admin"}
    )

    assert response.status_code == 400
    assert "password" in response.get_json()["message"]


def test_create_area_requires_nombre(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.post(
        "/api/plantas/1/areas", headers=headers, json={"estado": "operativa"}
    )

    assert response.status_code == 400
    assert "nombre" in response.get_json()["message"]


def test_update_area_requires_fields(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.put("/api/areas/101", headers=headers, json={})

    assert response.status_code == 400
    assert "Al menos un campo" in response.get_json()["message"]


def test_create_equipment_requires_nombre(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.post(
        "/api/areas/101/equipos", headers=headers, json={"estado": "operativo"}
    )

    assert response.status_code == 400
    assert "nombre" in response.get_json()["message"]


def test_update_equipment_rejects_long_status(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.put(
        "/api/equipos/1001", headers=headers, json={"estado": "x" * 60}
    )

    assert response.status_code == 400
    assert "estado" in response.get_json()["message"]


def test_create_system_requires_nombre(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.post(
        "/api/equipos/1001/sistemas", headers=headers, json={"estado": "operativo"}
    )

    assert response.status_code == 400
    assert "nombre" in response.get_json()["message"]


def test_update_system_rejects_long_status(validation_client, validation_auth_service):
    headers = _auth_headers(validation_auth_service)
    response = validation_client.put(
        "/api/sistemas/5001", headers=headers, json={"estado": "y" * 60}
    )

    assert response.status_code == 400
    assert "estado" in response.get_json()["message"]
