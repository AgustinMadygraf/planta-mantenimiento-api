"""Use case for deleting an area."""

from typing import Callable

from src.use_cases.ports.plant_repository import AreaRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class DeleteAreaUseCase:
    """Remove an area and its dependencies."""

    def __init__(
        self, repository: AreaRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(self, area_id: int) -> bool:
        with self._uow_factory() as uow:
            deleted = self._repository.delete_area(area_id, session=uow.session)
            if not deleted:
                uow.rollback()
                return False

            uow.commit()
            return True
