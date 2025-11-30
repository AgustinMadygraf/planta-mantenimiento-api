"""Entidad de usuario con claims de autorización."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class User:
    """Representa un usuario autenticable con claims."""

    username: str
    password_hash: str
    role: str
    areas: list[int] = field(default_factory=list)
    equipos: list[int] = field(default_factory=list)
