"""Initial schema aligned with SQLAlchemy models."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251201_01_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("areas", sa.Text(), nullable=True),
        sa.Column("equipos", sa.Text(), nullable=True),
    )

    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=150), nullable=False, unique=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="operativa",
        ),
    )

    op.create_table(
        "areas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="operativa",
        ),
        sa.ForeignKeyConstraint(
            ["plant_id"],
            ["plants.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("plant_id", "name", name="uq_area_name_per_plant"),
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="operativo",
        ),
        sa.ForeignKeyConstraint(
            ["area_id"],
            ["areas.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("area_id", "name", name="uq_equipment_name_per_area"),
    )

    op.create_table(
        "systems",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="operativo",
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"],
            ["equipment.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "equipment_id", "name", name="uq_system_name_per_equipment"
        ),
    )


def downgrade() -> None:
    op.drop_table("systems")
    op.drop_table("equipment")
    op.drop_table("areas")
    op.drop_table("plants")
    op.drop_table("users")
