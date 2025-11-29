"""Domain entity definitions for plants."""

from dataclasses import dataclass


@dataclass(slots=True)
class Plant:
    """Aggregate root representing a plant."""

    id: int | None
    name: str
    location: str | None
    status: str

    _VALID_STATUSES = {"operativa", "mantenimiento", "inactiva"}

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("El nombre de la planta no puede estar vacío")
        if self.status not in self._VALID_STATUSES:
            raise ValueError(f"Estado de planta inválido: {self.status}")

    @classmethod
    def create(cls, name: str, location: str | None = None) -> "Plant":
        """Factory to build a new plant with defaults."""

        return cls(id=None, name=name, location=location, status="operativa")

    def activate(self) -> None:
        self.status = "operativa"

    def deactivate(self) -> None:
        self.status = "inactiva"

    def mark_under_maintenance(self) -> None:
        self.status = "mantenimiento"
