"""Unit of Work contract to coordinate transactional work.

Use cases depend on this protocol to ensure multiple repository calls
share the same transactional boundary without knowing the underlying ORM.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitOfWork(Protocol):
    """Minimal contract for transactional coordination."""

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @property
    def session(self) -> object:
        """Opaque session/transaction handle usable by repositories."""
        ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


__all__ = ["UnitOfWork"]
