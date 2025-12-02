"""Funciones auxiliares compartidas para rutas de Flask."""

from __future__ import annotations

from typing import Any, Type

from flask import request
from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import BadRequest


def _require_json() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Cuerpo JSON inválido o ausente")
    return data


def _format_validation_errors(exc: ValidationError) -> str:
    errors = []
    for error in exc.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        errors.append(f"{loc or 'body'}: {error.get('msg')}")
    return "; ".join(errors) if errors else "Payload inválido"


def _validate_payload(payload: dict[str, Any], schema: Type[BaseModel]) -> dict[str, Any]:
    """Valida un payload contra un schema Pydantic y retorna datos filtrados."""
    try:
        validated = schema.model_validate(payload)
    except ValidationError as exc:
        raise BadRequest(f"Payload inválido: {_format_validation_errors(exc)}") from exc
    return validated.model_dump(exclude_none=True)
