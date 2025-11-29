"""Use case for creating new systems."""

from typing import Callable

from src.entities.system import System
from src.use_cases.ports.plant_repository import SystemRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class CreateSystemUseCase:
    """Create a system associated with equipment."""

    def __init__(
        self, repository: SystemRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, equipment_id: int, *, name: str, status: str | None = None
    ) -> System | None:
        with self._uow_factory() as uow:
            created = self._repository.create_system(
                equipment_id, name=name, status=status, session=uow.session
            )
            if created is None:
                uow.rollback()
                return None

            uow.commit()
            return created
