"""Domain entity definitions for equipment records."""

from dataclasses import dataclass


@dataclass(slots=True)
class Equipment:
    """Equipment located inside an area."""

    id: int | None
    area_id: int
    name: str
    status: str

    _VALID_STATUSES = {"operativo", "mantenimiento"}

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("El nombre del equipo no puede estar vacío")
        if self.status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de equipo inválido: {self.status}")

    @classmethod
    def create(cls, area_id: int, name: str, status: str = "operativo") -> "Equipment":
        return cls(id=None, area_id=area_id, name=name, status=status)

    def rename(self, new_name: str) -> None:
        self.name = new_name.strip()

    def change_status(self, status: str) -> None:
        if status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de equipo inválido: {status}")
        self.status = status
