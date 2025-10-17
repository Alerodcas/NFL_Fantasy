from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Annotated, Optional
from datetime import datetime
import re

# Esquema para la creación de un equipo
class TeamCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=128)]
    description: Annotated[Optional[str], Field(max_length=512)] = None
    logo_url: Annotated[Optional[HttpUrl], Field()] = None
    league_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Acepta letras, números y espacios; sin símbolos extraños
        if not re.match(r'^[A-Za-z0-9\s]+$', v):
            raise ValueError('El nombre del equipo solo puede contener letras, números y espacios')
        return v

# Esquema para actualizar un equipo
class TeamUpdate(BaseModel):
    name: Annotated[Optional[str], Field(min_length=3, max_length=128)] = None
    description: Annotated[Optional[str], Field(max_length=512)] = None
    logo_url: Annotated[Optional[HttpUrl], Field()] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[A-Za-z0-9\s]+$', v):
            raise ValueError('El nombre del equipo solo puede contener letras, números y espacios')
        return v

# Esquema para mostrar los datos de un equipo
class Team(BaseModel):
    id: int
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    league_id: int
    owner_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
