"""Handlers compartidos para respuestas de error JSON en Flask."""

from __future__ import annotations

from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException


def handle_http_exception(error: HTTPException):
    description = error.description or getattr(error, "name", None) or "HTTP error"
    status_code = error.code or 500
    return jsonify({"message": description}), status_code


def handle_unexpected_exception(error: Exception):
    current_app.logger.exception("Unhandled exception", exc_info=error)
    return jsonify({"message": "Internal server error"}), 500


__all__ = ["handle_http_exception", "handle_unexpected_exception"]
