import unittest

from src.infrastructure.sqlalchemy import mappers
from src.infrastructure.sqlalchemy.models import (
    AreaModel,
    EquipmentModel,
    PlantModel,
    SystemModel,
)


class SqlAlchemyMappersTestCase(unittest.TestCase):
    def test_plant_to_entity_maps_all_fields(self) -> None:
        model = PlantModel(id=7, name="Planta Central", location="Zona A", status="operativa")

        entity = mappers.plant_to_entity(model)

        self.assertEqual(entity.id, 7)
        self.assertEqual(entity.name, "Planta Central")
        self.assertEqual(entity.location, "Zona A")
        self.assertEqual(entity.status, "operativa")

    def test_area_to_entity_maps_parent_relation(self) -> None:
        model = AreaModel(id=5, plant_id=1, name="Área de pruebas", status="mantenimiento")

        entity = mappers.area_to_entity(model)

        self.assertEqual(entity.id, 5)
        self.assertEqual(entity.plant_id, 1)
        self.assertEqual(entity.name, "Área de pruebas")
        self.assertEqual(entity.status, "mantenimiento")

    def test_equipment_to_entity_maps_parent_relation(self) -> None:
        model = EquipmentModel(id=2, area_id=9, name="Compresor B", status="operativo")

        entity = mappers.equipment_to_entity(model)

        self.assertEqual(entity.id, 2)
        self.assertEqual(entity.area_id, 9)
        self.assertEqual(entity.name, "Compresor B")
        self.assertEqual(entity.status, "operativo")

    def test_system_to_entity_maps_parent_relation(self) -> None:
        model = SystemModel(id=4, equipment_id=11, name="Sistema X", status="operativo")

        entity = mappers.system_to_entity(model)

        self.assertEqual(entity.id, 4)
        self.assertEqual(entity.equipment_id, 11)
        self.assertEqual(entity.name, "Sistema X")
        self.assertEqual(entity.status, "operativo")


if __name__ == "__main__":
    unittest.main()
