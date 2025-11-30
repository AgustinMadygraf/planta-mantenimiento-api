"""
Path: src/infrastructure/sqlalchemy/models.py
"""

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


class Base(DeclarativeBase):
    "Declarative base para los modelos de persistencia."


class UserModel(Base):
    " Modelo ORM para usuarios."
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(100), nullable=False, unique=True)
    password_hash = mapped_column(String(255), nullable=False)
    role = mapped_column(String(50), nullable=False)
    areas = mapped_column(Text, nullable=True)
    equipos = mapped_column(Text, nullable=True)


class PlantModel(Base):
    "Modelo ORM para plantas."
    __tablename__ = "plants"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(150), nullable=False, unique=True)
    location = mapped_column(String(255), nullable=True)
    status = mapped_column(String(50), nullable=False, default="operativa")

    areas = relationship(
        "AreaModel",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AreaModel(Base):
    "Modelo ORM para áreas."
    __tablename__ = "areas"
    __table_args__ = (
        UniqueConstraint("plant_id", "name", name="uq_area_name_per_plant"),
    )

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), nullable=False
    )
    name = mapped_column(String(150), nullable=False)
    status = mapped_column(String(50), nullable=False, default="operativa")

    plant = relationship("PlantModel", back_populates="areas")
    equipment = relationship(
        "EquipmentModel",
        back_populates="area",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EquipmentModel(Base):
    "Modelo ORM para equipos."
    __tablename__ = "equipment"
    __table_args__ = (
        UniqueConstraint("area_id", "name", name="uq_equipment_name_per_area"),
    )

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_id = mapped_column(
        ForeignKey("areas.id", ondelete="CASCADE"), nullable=False
    )
    name = mapped_column(String(150), nullable=False)
    status = mapped_column(String(50), nullable=False, default="operativo")

    area = relationship("AreaModel", back_populates="equipment")
    systems = relationship(
        "SystemModel",
        back_populates="equipment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class SystemModel(Base):
    "Modelo ORM para sistemas."
    __tablename__ = "systems"
    __table_args__ = (
        UniqueConstraint("equipment_id", "name", name="uq_system_name_per_equipment"),
    )

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    name = mapped_column(String(150), nullable=False)
    status = mapped_column(String(50), nullable=False, default="operativo")

    equipment = relationship(
        "EquipmentModel", back_populates="systems"
    )


__all__ = [
    "Base",
    "UserModel",
    "PlantModel",
    "AreaModel",
    "EquipmentModel",
    "SystemModel",
]
