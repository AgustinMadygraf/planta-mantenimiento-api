"""Use case for updating an area."""

from typing import Callable

from src.entities.area import Area
from src.use_cases.ports.plant_repository import AreaRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class UpdateAreaUseCase:
    """Apply partial updates to an area."""

    def __init__(
        self, repository: AreaRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, area_id: int, *, name: str | None = None, status: str | None = None
    ) -> Area | None:
        with self._uow_factory() as uow:
            updated = self._repository.update_area(
                area_id, name=name, status=status, session=uow.session
            )
            if updated is None:
                uow.rollback()
                return None

            uow.commit()
            return updated
