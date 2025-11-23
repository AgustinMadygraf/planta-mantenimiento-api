"""Domain entity definitions for plants."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Plant:
    id: int
    name: str
    location: str
    status: str
