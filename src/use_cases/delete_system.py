"""Use case for deleting a system."""

from typing import Callable

from src.use_cases.ports.plant_repository import SystemRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class DeleteSystemUseCase:
    """Remove a system from its equipment."""

    def __init__(
        self, repository: SystemRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(self, system_id: int) -> bool:
        with self._uow_factory() as uow:
            deleted = self._repository.delete_system(system_id, session=uow.session)
            if not deleted:
                uow.rollback()
                return False

            uow.commit()
            return True
