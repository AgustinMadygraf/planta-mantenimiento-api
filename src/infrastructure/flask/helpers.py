"""Funciones auxiliares compartidas para rutas de Flask."""

from __future__ import annotations

from typing import Any

from flask import request
from werkzeug.exceptions import BadRequest


def _map_localized_fields(payload: dict[str, Any]) -> dict[str, Any]:
    mapped = {
        "name": payload.get("nombre"),
        "location": payload.get("ubicacion"),
        "status": payload.get("estado"),
    }
    return {key: value for key, value in mapped.items() if value is not None}


def _require_json() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Cuerpo JSON inválido o ausente")
    return data


def _require_fields(payload: dict[str, Any], required: list[str]) -> None:
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise BadRequest(f"Faltan campos obligatorios: {', '.join(missing)}")


def _require_nombre(payload: dict[str, Any]) -> str:
    nombre = payload.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        raise BadRequest("El campo 'nombre' es obligatorio")
    return nombre.strip()
