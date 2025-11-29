"""SQLAlchemy-backed Unit of Work implementation en infraestructura."""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from src.use_cases.ports.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Manage a SQLAlchemy session lifecycle for a use case."""

    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory
        self._session: Session | None = None
        self._completed = False

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._completed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        try:
            if self._session is None:
                return False

            if exc_type and not self._completed:
                self._session.rollback()
                self._completed = True
            elif not exc_type and not self._completed:
                self._session.commit()
                self._completed = True
        finally:
            if self._session is not None:
                self._session.close()
                self._session = None
        return False

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork session requested outside context")
        return self._session

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("commit() called without an active session")
        self._session.commit()
        self._completed = True

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("rollback() called without an active session")
        self._session.rollback()
        self._completed = True
