"""Simple providers for dependency injection in adapters."""

from src.interface_adapters.gateways.in_memory_plant_repository import InMemoryPlantRepository

plant_repository = InMemoryPlantRepository()
