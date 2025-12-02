"""Schemas Pydantic para operaciones con plantas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr, model_validator

_NAME_CONSTRAINT = constr(strip_whitespace=True, min_length=1, max_length=150)
_LOCATION_CONSTRAINT = constr(strip_whitespace=True, max_length=255)
_STATUS_CONSTRAINT = constr(strip_whitespace=True, min_length=1, max_length=50)


class LocalizedModel(BaseModel):
    "Base para aceptar alias en espanol pero usar campos ingleses internamente."

    model_config = ConfigDict(populate_by_name=True)


class UpdateSchema(LocalizedModel):
    @model_validator(mode="after")
    def ensure_at_least_one_field(self) -> "UpdateSchema":
        if not self.model_dump(exclude_none=True):
            raise ValueError("Al menos un campo debe enviarse para actualizar")
        return self


class PlantCreate(LocalizedModel):
    name: _NAME_CONSTRAINT = Field(..., alias="nombre")
    location: _LOCATION_CONSTRAINT | None = Field(None, alias="ubicacion")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")


class PlantUpdate(UpdateSchema):
    name: _NAME_CONSTRAINT | None = Field(None, alias="nombre")
    location: _LOCATION_CONSTRAINT | None = Field(None, alias="ubicacion")
    status: _STATUS_CONSTRAINT | None = Field(None, alias="estado")
