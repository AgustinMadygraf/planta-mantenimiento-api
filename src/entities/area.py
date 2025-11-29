"""Domain entity definitions for plant areas."""

from dataclasses import dataclass


@dataclass(slots=True)
class Area:
    """Area within a plant."""

    id: int | None
    plant_id: int
    name: str
    status: str

    _VALID_STATUSES = {"operativa", "mantenimiento"}

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("El nombre del área no puede estar vacío")
        if self.status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de área inválido: {self.status}")

    @classmethod
    def create(cls, plant_id: int, name: str, status: str = "operativa") -> "Area":
        return cls(id=None, plant_id=plant_id, name=name, status=status)

    def rename(self, new_name: str) -> None:
        self.name = new_name.strip()

    def change_status(self, status: str) -> None:
        if status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de área inválido: {status}")
        self.status = status
