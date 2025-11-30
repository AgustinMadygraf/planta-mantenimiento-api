"""
Path: src/infrastructure/user_repository.py
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from werkzeug.security import check_password_hash, generate_password_hash

from src.entities.user import User

DEFAULT_DEMO_USERS = (
    {
        "username": "superadmin",
        "password": "superadmin",
        "role": "superadministrador",
        "areas": [],
        "equipos": [],
    },
    {
        "username": "admin",
        "password": "admin",
        "role": "administrador",
        "areas": [101, 201],
        "equipos": [],
    },
    {
        "username": "maquinista",
        "password": "maquinista",
        "role": "maquinista",
        "areas": [],
        "equipos": [1001],
    },
    {
        "username": "invitado",
        "password": "invitado",
        "role": "invitado",
        "areas": [],
        "equipos": [],
    },
)


class UserRepository(Protocol):
    """Contrato mínimo para almacenar y recuperar usuarios."""

    def get_by_username(
        self, username: str, *, session: object | None = None
    ) -> User | None:
        "Recupera un usuario por su nombre de usuario."
        pass  # pylint: disable=unnecessary-pass

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role: str,
        areas: Sequence[int],
        equipos: Sequence[int],
        session: object | None = None,
    ) -> User:
        "Crea un nuevo usuario."
        pass  # pylint: disable=unnecessary-pass

    def list_users(self, *, session: object | None = None) -> Sequence[User]:
        "Lista todos los usuarios."
        pass  # pylint: disable=unnecessary-pass


class InMemoryUserRepository(UserRepository):
    """Repositorio simple para pruebas y fallback local."""

    def __init__(self, initial: Sequence[User] | None = None) -> None:
        self._users: dict[str, User] = {user.username: user for user in initial or ()}

    @classmethod
    def with_defaults(cls) -> "InMemoryUserRepository":
        "Crea un repositorio con usuarios de demostración."
        repo = cls()
        for user in DEFAULT_DEMO_USERS:
            repo.create_user(
                username=user["username"],
                password=user["password"],
                role=user["role"],
                areas=user["areas"],
                equipos=user["equipos"],
            )
        return repo

    def get_by_username(
        self, username: str, *, session: object | None = None
    ) -> User | None:
        return self._users.get(username)

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role: str,
        areas: Sequence[int],
        equipos: Sequence[int],
        session: object | None = None,
    ) -> User:
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            areas=list(areas),
            equipos=list(equipos),
        )
        self._users[username] = user
        return user

    def list_users(self, *, session: object | None = None) -> Sequence[User]:
        return list(self._users.values())

    def verify_credentials(self, username: str, password: str) -> User | None:
        "Verifica las credenciales y devuelve el usuario si son correctas."
        user = self.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
