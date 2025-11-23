"""Domain entity definitions for system records."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class System:
    id: int
    equipment_id: int
    name: str
    status: str
