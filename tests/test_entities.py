import unittest

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.system import System


class EntityRenameValidationTestCase(unittest.TestCase):
    def test_area_rename_trims_and_updates(self) -> None:
        area = Area.create(plant_id=1, name="Área Original", status="operativa")

        area.rename("  Área Nueva  ")

        self.assertEqual(area.name, "Área Nueva")

    def test_area_rename_rejects_blank(self) -> None:
        area = Area.create(plant_id=1, name="Área Original", status="operativa")

        with self.assertRaises(ValueError):
            area.rename("   ")

    def test_equipment_rename_trims_and_updates(self) -> None:
        equipment = Equipment.create(area_id=2, name="Equipo A", status="operativo")

        equipment.rename("  Equipo B  ")

        self.assertEqual(equipment.name, "Equipo B")

    def test_equipment_rename_rejects_blank(self) -> None:
        equipment = Equipment.create(area_id=2, name="Equipo A", status="operativo")

        with self.assertRaises(ValueError):
            equipment.rename("\n\t ")

    def test_system_rename_trims_and_updates(self) -> None:
        system = System.create(equipment_id=3, name="Sistema 1", status="operativo")

        system.rename(" Sistema 2 ")

        self.assertEqual(system.name, "Sistema 2")

    def test_system_rename_rejects_blank(self) -> None:
        system = System.create(equipment_id=3, name="Sistema 1", status="operativo")

        with self.assertRaises(ValueError):
            system.rename("\t")


if __name__ == "__main__":
    unittest.main()
