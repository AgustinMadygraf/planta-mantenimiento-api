"""Schema Pydantic para login."""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, constr


_USERNAME = constr(strip_whitespace=True, min_length=1, max_length=150)
_PASSWORD = constr(min_length=1, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: _USERNAME = Field(..., alias="username")
    password: _PASSWORD = Field(..., alias="password")
