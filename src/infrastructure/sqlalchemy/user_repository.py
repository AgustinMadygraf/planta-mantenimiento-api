"""Repositorio de usuarios persistentes respaldado por SQLAlchemy."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from src.infrastructure.flask.auth import AuthUser
from src.infrastructure.sqlalchemy.models import UserModel
from src.infrastructure.sqlalchemy.session import SessionFactory


class UserRepository(Protocol):
    def get_user(self, username: str) -> AuthUser | None: ...

    def upsert_user(self, user: AuthUser) -> AuthUser: ...


class SqlAlchemyUserRepository(UserRepository):
    """Acceso a la tabla de usuarios con persistencia y hashing seguro."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:  # pragma: no cover - la rama principal se usa en runtime
            with self._session_factory() as new_session:
                yield new_session

    @contextmanager
    def _transactional_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:  # pragma: no cover - la rama principal se usa en runtime
            with self._session_factory() as new_session, new_session.begin():
                yield new_session

    def get_user(self, username: str, *, session: Session | None = None) -> AuthUser | None:
        with self._session_scope(session) as db:
            row = db.execute(
                select(UserModel).where(UserModel.username == username)
            ).scalar_one_or_none()
            if row is None:
                return None

            return AuthUser(
                username=row.username,
                password_hash=row.password_hash,
                role=row.role,
                areas=list(row.areas or []),
                equipos=list(row.equipos or []),
            )

    def upsert_user(self, user: AuthUser, *, session: Session | None = None) -> AuthUser:
        with self._transactional_scope(session) as db:
            existing = db.execute(
                select(UserModel).where(UserModel.username == user.username)
            ).scalar_one_or_none()

            if existing is None:
                model = UserModel(
                    username=user.username,
                    password_hash=user.password_hash,
                    role=user.role,
                    areas=user.areas,
                    equipos=user.equipos,
                )
                db.add(model)
            else:
                existing.password_hash = user.password_hash
                existing.role = user.role
                existing.areas = user.areas
                existing.equipos = user.equipos
                model = existing

            db.flush()

            return AuthUser(
                username=model.username,
                password_hash=model.password_hash,
                role=model.role,
                areas=list(model.areas or []),
                equipos=list(model.equipos or []),
            )

    def bootstrap_demo_users(self) -> None:
        """Crea usuarios de demostración con contraseñas hasheadas si no existen."""

        demo = (
            AuthUser(
                username="superadmin",
                password_hash=generate_password_hash("superadmin"),
                role="superadministrador",
                areas=[],
                equipos=[],
            ),
            AuthUser(
                username="admin",
                password_hash=generate_password_hash("admin"),
                role="administrador",
                areas=[101, 201],
                equipos=[],
            ),
            AuthUser(
                username="maquinista",
                password_hash=generate_password_hash("maquinista"),
                role="maquinista",
                areas=[],
                equipos=[1001],
            ),
            AuthUser(
                username="invitado",
                password_hash=generate_password_hash("invitado"),
                role="invitado",
                areas=[],
                equipos=[],
            ),
        )

        with self._session_factory() as db, db.begin():
            for user in demo:
                self.upsert_user(user, session=db)

