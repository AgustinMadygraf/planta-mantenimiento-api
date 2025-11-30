"""Cobertura básica de autenticación y autorización en Flask."""

from __future__ import annotations

import pytest
from flask import Flask

from src.infrastructure.flask.auth import AuthClaims, AuthService, ScopeAuthorizer
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
    return AuthService(secret_key="test-secret", token_ttl_seconds=3600)


@pytest.fixture()
def flask_app(auth_service: AuthService) -> Flask:
    repository = InMemoryPlantRepository()
    uow_factory = DummyUnitOfWork

    scope = ScopeAuthorizer(
        get_area=GetAreaUseCase(repository).execute,
        get_equipment=GetEquipmentUseCase(repository).execute,
        get_system=GetSystemUseCase(repository).execute,
    )

    app = Flask(__name__)
    app.register_blueprint(
        build_blueprint(
            repository,
            uow_factory,
            auth_service=auth_service,
            scope_authorizer=scope,
        )
    )
    app.testing = True
    return app


@pytest.fixture()
def client(flask_app: Flask):
    return flask_app.test_client()


def _auth_headers(auth_service: AuthService, username: str) -> dict[str, str]:
    token = auth_service.issue_token(username, username)
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_token_and_claims(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "token" in body
    assert body["user"]["role"] == "administrador"


def test_rejects_requests_without_token(client):
    response = client.get("/api/plantas")
    assert response.status_code == 401


def test_accepts_lowercase_bearer_token(client, auth_service):
    headers = {"Authorization": f"bearer {auth_service.issue_token('admin', 'admin')}"}

    response = client.get("/api/plantas", headers=headers)

    assert response.status_code == 200


def test_admin_cannot_delete_plant(client, auth_service):
    headers = _auth_headers(auth_service, "admin")
    response = client.delete("/api/plantas/1", headers=headers)
    assert response.status_code == 403


def test_admin_only_sees_scoped_areas(client, auth_service):
    headers = _auth_headers(auth_service, "admin")
    response = client.get("/api/plantas/1/areas", headers=headers)
    assert response.status_code == 200
    body = response.get_json()
    assert {area["id"] for area in body} == {101}


def test_maquinista_can_manage_scoped_equipment(client, auth_service):
    headers = _auth_headers(auth_service, "maquinista")
    response = client.put(
        "/api/equipos/1001",
        headers=headers,
        json={"nombre": "Compresor A v2"},
    )
    assert response.status_code == 200

    forbidden = client.put(
        "/api/equipos/2001",
        headers=headers,
        json={"nombre": "Fuera de alcance"},
    )
    assert forbidden.status_code == 403


def test_filter_areas_ignores_missing_equipment_in_claims():
    repository = InMemoryPlantRepository()
    scope = ScopeAuthorizer(
        get_area=GetAreaUseCase(repository).execute,
        get_equipment=GetEquipmentUseCase(repository).execute,
        get_system=GetSystemUseCase(repository).execute,
    )

    claims = AuthClaims(
        username="maquinista",
        role="maquinista",
        areas=[],
        equipos=[9999, 1001],
    )

    areas = repository.list_areas(1)
    scoped = scope.filter_areas(claims, 1, areas)

    assert {area.id for area in scoped} == {101}
