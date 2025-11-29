"""Domain entity definitions for system records."""

from dataclasses import dataclass


@dataclass(slots=True)
class System:
    """Technical system attached to equipment."""

    id: int | None
    equipment_id: int
    name: str
    status: str

    _VALID_STATUSES = {"operativo", "mantenimiento"}

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("El nombre del sistema no puede estar vacío")
        if self.status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de sistema inválido: {self.status}")

    @classmethod
    def create(
        cls, equipment_id: int, name: str, status: str = "operativo"
    ) -> "System":
        return cls(id=None, equipment_id=equipment_id, name=name, status=status)

    def rename(self, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("El nombre del sistema no puede estar vacío")
        self.name = new_name

    def change_status(self, status: str) -> None:
        if status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de sistema inválido: {status}")
        self.status = status
