import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.sqlalchemy import Base
from src.infrastructure.sqlalchemy.models import AreaModel, EquipmentModel, PlantModel, SystemModel
from src.infrastructure.sqlalchemy.plant_repository import SqlAlchemyPlantRepository


@pytest.fixture()
def engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(engine, expire_on_commit=False, future=True)


def test_create_and_list_plants_with_defaults(session_factory):
    repo = SqlAlchemyPlantRepository(session_factory)

    created = repo.create_plant(name="Central", location="Norte")
    second = repo.create_plant(name="Backup")

    plants = repo.list_plants()

    assert {plant.name for plant in plants} == {"Central", "Backup"}
    assert created.location == "Norte"
    assert second.status == "operativa"


def test_area_crud_requires_existing_plant(session_factory):
    repo = SqlAlchemyPlantRepository(session_factory)
    plant = repo.create_plant(name="Planta A")

    area = repo.create_area(plant.id, name="Área 1")
    updated = repo.update_area(area.id, name="Área 1B", status="mantenimiento")

    missing_parent = repo.create_area(9999, name="Sin planta")

    assert area.name == "Área 1"
    assert updated.name == "Área 1B"
    assert updated.status == "mantenimiento"
    assert missing_parent is None


def test_equipment_and_system_crud_with_cascades(session_factory, engine):
    repo = SqlAlchemyPlantRepository(session_factory)
    plant = repo.create_plant(name="Planta A")
    area = repo.create_area(plant.id, name="Área X")

    equipment = repo.create_equipment(area.id, name="Compresor")
    system = repo.create_system(equipment.id, name="Sistema A")
    updated_system = repo.update_system(system.id, status="mantenimiento")

    listed_equipment = repo.list_equipment(area.id)
    listed_systems = repo.list_systems(equipment.id)

    assert equipment.status == "operativo"
    assert updated_system.status == "mantenimiento"
    assert [eq.name for eq in listed_equipment] == ["Compresor"]
    assert [sys.name for sys in listed_systems] == ["Sistema A"]

    assert repo.delete_system(system.id) is True
    assert repo.list_systems(equipment.id) == []

    assert repo.delete_equipment(equipment.id) is True
    assert repo.list_equipment(area.id) == []

    assert repo.delete_area(area.id) is True
    assert repo.list_areas(plant.id) == []

    # Plant deletion should succeed once children are removed
    assert repo.delete_plant(plant.id) is True

    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(PlantModel)) == 0
