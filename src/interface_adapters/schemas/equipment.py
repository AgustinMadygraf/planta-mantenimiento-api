"""Schemas Pydantic para operaciones con equipos."""

from __future__ import annotations

from pydantic import Field

from .plant import LocalizedModel, UpdateSchema, _NAME_CONSTRAINT, _STATUS_CONSTRAINT


class EquipmentCreate(LocalizedModel):
    name: _NAME_CONSTRAINT = Field(..., alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")


class EquipmentUpdate(UpdateSchema):
    name: _NAME_CONSTRAINT | None = Field(None, alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")
