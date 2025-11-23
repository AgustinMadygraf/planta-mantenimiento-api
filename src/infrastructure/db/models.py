"""Modelos ORM para MySQL usando SQLAlchemy Declarative."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PlantModel(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="operativa")

    areas: Mapped[list["AreaModel"]] = relationship(
        "AreaModel",
        back_populates="plant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AreaModel(Base):
    __tablename__ = "areas"
    __table_args__ = (UniqueConstraint("plant_id", "name", name="uq_area_name_per_plant"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="operativa")

    plant: Mapped[PlantModel] = relationship("PlantModel", back_populates="areas")
    equipment: Mapped[list["EquipmentModel"]] = relationship(
        "EquipmentModel",
        back_populates="area",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EquipmentModel(Base):
    __tablename__ = "equipment"
    __table_args__ = (
        UniqueConstraint("area_id", "name", name="uq_equipment_name_per_area"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_id: Mapped[int] = mapped_column(
        ForeignKey("areas.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="operativo")

    area: Mapped[AreaModel] = relationship("AreaModel", back_populates="equipment")
    systems: Mapped[list["SystemModel"]] = relationship(
        "SystemModel",
        back_populates="equipment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SystemModel(Base):
    __tablename__ = "systems"
    __table_args__ = (
        UniqueConstraint("equipment_id", "name", name="uq_system_name_per_equipment"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="operativo")

    equipment: Mapped[EquipmentModel] = relationship(
        "EquipmentModel", back_populates="systems"
    )
