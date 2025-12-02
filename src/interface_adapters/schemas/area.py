"""Schemas Pydantic para operaciones con áreas."""

from __future__ import annotations

from pydantic import Field

from .plant import UpdateSchema, LocalizedModel, _STATUS_CONSTRAINT, _NAME_CONSTRAINT


class AreaCreate(LocalizedModel):
    name: _NAME_CONSTRAINT = Field(..., alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")


class AreaUpdate(UpdateSchema):
    name: _NAME_CONSTRAINT | None = Field(None, alias="nombre")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")
