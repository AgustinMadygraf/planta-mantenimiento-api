"""Domain entity definitions for equipment records."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Equipment:
    id: int
    area_id: int
    name: str
    status: str
