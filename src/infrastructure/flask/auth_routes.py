"""Blueprint de autenticación para emisión de tokens demo."""

from __future__ import annotations

from flask import Blueprint, jsonify

from src.infrastructure.flask.auth import AuthService
from src.infrastructure.flask.helpers import _require_fields, _require_json


def build_auth_blueprint(auth_service: AuthService) -> Blueprint:
    auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

    @auth_bp.post("/login")
    def login():
        payload = _require_json()
        _require_fields(payload, ["username", "password"])

        token = auth_service.issue_token(payload["username"], payload["password"])

        claims = auth_service.decode_token(token)
        return jsonify(
            {
                "token": token,
                "user": {
                    "username": claims.username,
                    "role": claims.role,
                    "areas": claims.areas,
                    "equipos": claims.equipos,
                },
            }
        )

    return auth_bp
