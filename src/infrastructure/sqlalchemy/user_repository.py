"""
Path: src/infrastructure/sqlalchemy/user_repository.py
"""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import contextmanager
import json

from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from src.entities.user import User
from src.infrastructure.sqlalchemy import mappers
from src.infrastructure.sqlalchemy.models import UserModel
from src.infrastructure.sqlalchemy.session import SessionFactory
from src.infrastructure.user_repository import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    """Persiste usuarios y claims usando SQLAlchemy."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:
            with self._session_factory() as new_session:
                yield new_session

    @contextmanager
    def _transactional_scope(self, session: Session | None):
        if session is not None:
            yield session
        else:
            with self._session_factory() as new_session, new_session.begin():
                yield new_session

    def get_by_username(
        self, username: str, *, session: Session | None = None
    ) -> User | None:
        with self._session_scope(session) as db:
            result = db.execute(
                select(UserModel).where(UserModel.username == username)
            ).scalar_one_or_none()
            if result is None:
                return None
            return mappers.user_to_entity(result)

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role: str,
        areas: Sequence[int],
        equipos: Sequence[int],
        session: Session | None = None,
    ) -> User:
        with self._transactional_scope(session) as db:
            model = UserModel(
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                areas=json.dumps(areas) if areas else "",
                equipos=json.dumps(equipos) if equipos else "",
            )
            db.add(model)
            db.flush()
            return mappers.user_to_entity(model)

    def list_users(self, *, session: Session | None = None) -> Sequence[User]:
        with self._session_scope(session) as db:
            rows = db.execute(select(UserModel)).scalars().all()
            return [mappers.user_to_entity(row) for row in rows]
