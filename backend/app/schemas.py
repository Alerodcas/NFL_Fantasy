from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated
import re

# Esquema para la creación de un usuario
class UserCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    email: EmailStr
    alias: Annotated[str, Field(min_length=1, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=12)]
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # Verificar longitud en bytes para bcrypt
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

# Esquema para mostrar los datos de un usuario (sin contraseña)
class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    alias: str
    role: str
    account_status: str

    class Config:
        from_attributes = True

# Esquema para actualizar el perfil del usuario
class UserUpdate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    alias: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    password: Annotated[str, Field(min_length=8, max_length=12)] | None = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:  # Solo validar si se proporciona una contraseña
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one digit')
        return v

# Esquema para el token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

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
