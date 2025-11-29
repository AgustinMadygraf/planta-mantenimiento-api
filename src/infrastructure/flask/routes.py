"""Rutas HTTP basadas en Flask ubicadas en infraestructura."""

from __future__ import annotations

from typing import Callable

from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.areas import build_areas_blueprint
from src.infrastructure.flask.equipment import build_equipment_blueprint
from src.infrastructure.flask.plants import build_plants_blueprint
from src.infrastructure.flask.systems import build_systems_blueprint
from src.use_cases.create_area import CreateAreaUseCase
from src.use_cases.create_equipment import CreateEquipmentUseCase
from src.use_cases.create_plant import CreatePlantUseCase
from src.use_cases.create_system import CreateSystemUseCase
from src.use_cases.delete_area import DeleteAreaUseCase
from src.use_cases.delete_equipment import DeleteEquipmentUseCase
from src.use_cases.delete_plant import DeletePlantUseCase
from src.use_cases.delete_system import DeleteSystemUseCase
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.get_plant import GetPlantUseCase
from src.use_cases.list_area_equipment import ListAreaEquipmentUseCase
from src.use_cases.list_equipment_systems import ListEquipmentSystemsUseCase
from src.use_cases.list_plant_areas import ListPlantAreasUseCase
from src.use_cases.list_plants import ListPlantsUseCase
from src.use_cases.ports.plant_repository import PlantDataRepository
from src.use_cases.ports.unit_of_work import UnitOfWork
from src.use_cases.update_area import UpdateAreaUseCase
from src.use_cases.update_equipment import UpdateEquipmentUseCase
from src.use_cases.update_plant import UpdatePlantUseCase
from src.use_cases.update_system import UpdateSystemUseCase


def build_blueprint(
    repository: PlantDataRepository, uow_factory: Callable[[], UnitOfWork]
) -> Blueprint:
    "Construye el Blueprint de Flask con las rutas de la API."
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    @api_bp.errorhandler(BadRequest)
    def handle_bad_request(error: BadRequest):
        return jsonify({"detail": error.description}), 400

    @api_bp.errorhandler(NotFound)
    def handle_not_found(error: NotFound):
        return jsonify({"detail": error.description}), 404

    list_plants_use_case = ListPlantsUseCase(repository)
    get_plant_use_case = GetPlantUseCase(repository)
    create_plant_use_case = CreatePlantUseCase(repository, uow_factory)
    update_plant_use_case = UpdatePlantUseCase(repository, uow_factory)
    delete_plant_use_case = DeletePlantUseCase(repository, uow_factory)
    list_plant_areas_use_case = ListPlantAreasUseCase(repository)
    create_area_use_case = CreateAreaUseCase(repository, uow_factory)

    get_area_use_case = GetAreaUseCase(repository)
    update_area_use_case = UpdateAreaUseCase(repository, uow_factory)
    delete_area_use_case = DeleteAreaUseCase(repository, uow_factory)
    list_area_equipment_use_case = ListAreaEquipmentUseCase(repository)
    create_equipment_use_case = CreateEquipmentUseCase(repository, uow_factory)

    get_equipment_use_case = GetEquipmentUseCase(repository)
    update_equipment_use_case = UpdateEquipmentUseCase(repository, uow_factory)
    delete_equipment_use_case = DeleteEquipmentUseCase(repository, uow_factory)
    list_equipment_systems_use_case = ListEquipmentSystemsUseCase(repository)
    create_system_use_case = CreateSystemUseCase(repository, uow_factory)

    update_system_use_case = UpdateSystemUseCase(repository, uow_factory)
    delete_system_use_case = DeleteSystemUseCase(repository, uow_factory)

    plants_bp = build_plants_blueprint(
        list_plants_use_case,
        get_plant_use_case,
        create_plant_use_case,
        update_plant_use_case,
        delete_plant_use_case,
        list_plant_areas_use_case,
        create_area_use_case,
    )

    areas_bp = build_areas_blueprint(
        get_area_use_case,
        update_area_use_case,
        delete_area_use_case,
        list_area_equipment_use_case,
        create_equipment_use_case,
    )

    equipment_bp = build_equipment_blueprint(
        get_equipment_use_case,
        update_equipment_use_case,
        delete_equipment_use_case,
        list_equipment_systems_use_case,
        create_system_use_case,
    )

    systems_bp = build_systems_blueprint(update_system_use_case, delete_system_use_case)

    api_bp.register_blueprint(plants_bp)
    api_bp.register_blueprint(areas_bp)
    api_bp.register_blueprint(equipment_bp)
    api_bp.register_blueprint(systems_bp)

    return api_bp
