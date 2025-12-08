"""Handlers compartidos para respuestas de error JSON en Flask."""

from __future__ import annotations

from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException


def handle_http_exception(error: HTTPException):
    fallback_messages = {
        400: "Solicitud inválida",
        401: "No autorizado",
        403: "Prohibido",
        404: "Recurso no encontrado",
        405: "Método no permitido",
    }

    description = (
        error.description
        or fallback_messages.get(error.code or 0)
        or getattr(error, "name", None)
        or "Error HTTP"
    )
    status_code = error.code or 500
    return jsonify({"message": description}), status_code


def handle_unexpected_exception(error: Exception):
    current_app.logger.exception("Unhandled exception", exc_info=error)
    return jsonify({"message": "Error interno del servidor"}), 500


__all__ = ["handle_http_exception", "handle_unexpected_exception"]
