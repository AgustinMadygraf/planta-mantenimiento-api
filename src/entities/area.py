"""Domain entity definitions for plant areas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Area:
    id: int
    plant_id: int
    name: str
    status: str
