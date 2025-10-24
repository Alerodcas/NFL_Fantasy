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
    email: str
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


# Esquema para el token de acceso (login)
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str


