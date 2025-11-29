"""Use case for updating system information."""

from typing import Callable

from src.entities.system import System
from src.use_cases.ports.plant_repository import SystemRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class UpdateSystemUseCase:
    """Apply updates to a system record."""

    def __init__(
        self, repository: SystemRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, system_id: int, *, name: str | None = None, status: str | None = None
    ) -> System | None:
        with self._uow_factory() as uow:
            updated = self._repository.update_system(
                system_id, name=name, status=status, session=uow.session
            )
            if updated is None:
                uow.rollback()
                return None

            uow.commit()
            return updated
