"""Validaciones de configuración obligatoria para autenticación."""

from __future__ import annotations

import pytest

from src.infrastructure.flask.auth import AuthService
from src.infrastructure.flask.routes import build_blueprint
from src.interface_adapters.gateways.in_memory_plant_repository import (
    InMemoryPlantRepository,
)
from src.use_cases.ports.unit_of_work import UnitOfWork


class _DummyUnitOfWork(UnitOfWork):
    def __enter__(self):  # pragma: no cover - requerido por protocolo
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover - no-op
        return False

    def commit(self):  # pragma: no cover - no-op
        return None

    def rollback(self):  # pragma: no cover - no-op
        return None

    @property
    def session(self):  # pragma: no cover - no session para pruebas
        return None


def test_auth_service_requires_secret_key(monkeypatch):
    monkeypatch.delenv("AUTH_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="AUTH_SECRET_KEY es obligatorio"):
        AuthService()


def test_build_blueprint_fails_without_secret_key(monkeypatch):
    monkeypatch.delenv("AUTH_SECRET_KEY", raising=False)

    repository = InMemoryPlantRepository()

    with pytest.raises(RuntimeError, match="AUTH_SECRET_KEY es obligatorio"):
        build_blueprint(repository, _DummyUnitOfWork)
