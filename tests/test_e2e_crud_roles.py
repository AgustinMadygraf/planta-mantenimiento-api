"""Pruebas integrales de CRUD y roles usando la pila Flask completa."""

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
def api_client():
    repository = InMemoryPlantRepository()
    auth_service = AuthService(secret_key="integration-secret")
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
    return app.test_client()


def _login(client, username: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.data
    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_superadmin_full_crud_flow(api_client):
    headers = _login(api_client, "superadmin", "superadmin")

    created_plant = api_client.post(
        "/api/plantas", headers=headers, json={"nombre": "Nueva Planta"}
    )
    assert created_plant.status_code == 201
    plant_id = created_plant.get_json()["id"]

    created_area = api_client.post(
        f"/api/plantas/{plant_id}/areas",
        headers=headers,
        json={"nombre": "Área Principal"},
    )
    assert created_area.status_code == 201
    area_id = created_area.get_json()["id"]

    created_equipment = api_client.post(
        f"/api/areas/{area_id}/equipos",
        headers=headers,
        json={"nombre": "Equipo Demo"},
    )
    assert created_equipment.status_code == 201
    equipment_id = created_equipment.get_json()["id"]

    created_system = api_client.post(
        f"/api/equipos/{equipment_id}/sistemas",
        headers=headers,
        json={"nombre": "Sistema Demo"},
    )
    assert created_system.status_code == 201
    system_id = created_system.get_json()["id"]

    updated_plant = api_client.put(
        f"/api/plantas/{plant_id}",
        headers=headers,
        json={"nombre": "Planta Actualizada"},
    )
    assert updated_plant.status_code == 200
    assert updated_plant.get_json()["nombre"] == "Planta Actualizada"

    updated_area = api_client.put(
        f"/api/areas/{area_id}",
        headers=headers,
        json={"nombre": "Área Actualizada"},
    )
    assert updated_area.status_code == 200
    assert updated_area.get_json()["nombre"] == "Área Actualizada"

    updated_equipment = api_client.put(
        f"/api/equipos/{equipment_id}",
        headers=headers,
        json={"nombre": "Equipo Actualizado"},
    )
    assert updated_equipment.status_code == 200
    assert updated_equipment.get_json()["nombre"] == "Equipo Actualizado"

    updated_system = api_client.put(
        f"/api/sistemas/{system_id}",
        headers=headers,
        json={"nombre": "Sistema Actualizado"},
    )
    assert updated_system.status_code == 200
    assert updated_system.get_json()["nombre"] == "Sistema Actualizado"

    assert api_client.delete(
        f"/api/sistemas/{system_id}", headers=headers
    ).status_code == 204
    assert api_client.delete(
        f"/api/equipos/{equipment_id}", headers=headers
    ).status_code == 204
    assert api_client.delete(f"/api/areas/{area_id}", headers=headers).status_code == 204
    assert api_client.delete(f"/api/plantas/{plant_id}", headers=headers).status_code == 204

    deleted = api_client.get(f"/api/plantas/{plant_id}", headers=headers)
    assert deleted.status_code == 404


def test_admin_respects_scope_across_crud(api_client):
    super_headers = _login(api_client, "superadmin", "superadmin")
    outside_area_equipment = api_client.post(
        "/api/areas/301/equipos",
        headers=super_headers,
        json={"nombre": "Equipo Planta 3"},
    )
    assert outside_area_equipment.status_code == 201
    outside_equipment_id = outside_area_equipment.get_json()["id"]

    headers = _login(api_client, "admin", "admin")

    forbidden_plant = api_client.post(
        "/api/plantas", headers=headers, json={"nombre": "No permitido"}
    )
    assert forbidden_plant.status_code == 403

    created_area = api_client.post(
        "/api/plantas/1/areas", headers=headers, json={"nombre": "Área Admin"}
    )
    assert created_area.status_code == 201

    out_of_scope_area = api_client.post(
        "/api/plantas/3/areas", headers=headers, json={"nombre": "Fuera"}
    )
    assert out_of_scope_area.status_code == 403

    updated_equipment = api_client.put(
        "/api/equipos/1001",
        headers=headers,
        json={"nombre": "Equipo en alcance"},
    )
    assert updated_equipment.status_code == 200

    blocked_equipment = api_client.put(
        f"/api/equipos/{outside_equipment_id}",
        headers=headers,
        json={"nombre": "Equipo fuera de alcance"},
    )
    assert blocked_equipment.status_code == 403

    cannot_delete_plant = api_client.delete("/api/plantas/1", headers=headers)
    assert cannot_delete_plant.status_code == 403


def test_maquinista_only_manages_assigned_equipment(api_client):
    headers = _login(api_client, "maquinista", "maquinista")

    areas = api_client.get("/api/plantas/1/areas", headers=headers)
    assert areas.status_code == 200
    assert {area["id"] for area in areas.get_json()} == {101}

    allowed_update = api_client.put(
        "/api/equipos/1001",
        headers=headers,
        json={"nombre": "Equipo Maquinista"},
    )
    assert allowed_update.status_code == 200

    forbidden_update = api_client.put(
        "/api/equipos/1002",
        headers=headers,
        json={"nombre": "No permitido"},
    )
    assert forbidden_update.status_code == 403

    new_system = api_client.post(
        "/api/equipos/1001/sistemas",
        headers=headers,
        json={"nombre": "Sistema Operador"},
    )
    assert new_system.status_code == 201

    created_system_id = new_system.get_json()["id"]
    assert (
        api_client.delete(f"/api/sistemas/{created_system_id}", headers=headers).status_code
        == 204
    )

    cannot_create_equipment = api_client.post(
        "/api/areas/101/equipos",
        headers=headers,
        json={"nombre": "Equipo bloqueado"},
    )
    assert cannot_create_equipment.status_code == 403


def test_guest_is_read_only(api_client):
    headers = _login(api_client, "invitado", "invitado")

    plants = api_client.get("/api/plantas", headers=headers)
    assert plants.status_code == 200
    assert len(plants.get_json()) > 0

    cannot_update = api_client.put(
        "/api/plantas/1", headers=headers, json={"nombre": "No permitido"}
    )
    assert cannot_update.status_code == 403

    cannot_create_area = api_client.post(
        "/api/plantas/1/areas", headers=headers, json={"nombre": "Área Invitado"}
    )
    assert cannot_create_area.status_code == 403
