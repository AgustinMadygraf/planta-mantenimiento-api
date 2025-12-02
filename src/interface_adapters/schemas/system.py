"""Schemas Pydantic para operaciones con sistemas."""

from __future__ import annotations

from pydantic import Field

from .plant import LocalizedModel, UpdateSchema, _NAME_CONSTRAINT, _STATUS_CONSTRAINT


class SystemCreate(LocalizedModel):
    name: _NAME_CONSTRAINT = Field(..., alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")


class SystemUpdate(UpdateSchema):
    name: _NAME_CONSTRAINT | None = Field(None, alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")
