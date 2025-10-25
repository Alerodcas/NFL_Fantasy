from pydantic import BaseModel, Field, field_validator, validator, model_validator, ConfigDict
from typing import Optional, Literal, List
from datetime import date, datetime

_ALLOWED_TEAM_SIZES = {4, 6, 8, 10, 12, 14, 16, 18, 20}

class LeagueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    max_teams: int
    password: str = Field(..., min_length=8, max_length=12)
    playoff_format: Literal[4, 6]
    allow_decimal_scoring: bool = True

    team_id: int = Field(..., ge=1)

    @field_validator("max_teams")
    @classmethod
    def check_team_sizes(cls, v: int):
        if v not in _ALLOWED_TEAM_SIZES:
            raise ValueError(f"max_teams must be one of {_ALLOWED_TEAM_SIZES}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        import re
        if not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9]{8,12}", v):
            raise ValueError(
                "Password must be 8–12 chars, alphanumeric, include at least one lowercase and one uppercase."
            )
        return v


class LeagueCreated(BaseModel):
    id: int
    uuid: Optional[str] = None
    name: str
    status: str
    max_teams: int
    playoff_format: int
    allow_decimal_scoring: bool
    season_id: int
    slots_remaining: int
    commissioner_team_id: int


class WeekCreate(BaseModel):
    week_number: int
    start_date: date
    end_date: date
    
    @field_validator('week_number')
    @classmethod
    def validate_week_number(cls, v):
        if v < 1:
            raise ValueError('El número de semana debe ser mayor a 0')
        return v

class WeekResponse(BaseModel):
    id: int
    season_id: int
    week_number: int
    start_date: date
    end_date: date
    
    model_config = ConfigDict(from_attributes=True)

class SeasonCreate(BaseModel):
    name: str
    week_count: int
    start_date: date
    end_date: date
    is_current: bool = False
    weeks: List[WeekCreate] = []
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El nombre es requerido')
        if len(v) > 100:
            raise ValueError('El nombre no puede exceder 100 caracteres')
        return v.strip()
    
    @field_validator('week_count')
    @classmethod
    def validate_week_count(cls, v):
        if v < 1 or v > 52:
            raise ValueError('La cantidad de semanas debe estar entre 1 y 52')
        return v
    
    @model_validator(mode='after')
    def validate_model(self):
        # Validar fechas
        if self.end_date <= self.start_date:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        
        # Validar cantidad de semanas
        if self.weeks and len(self.weeks) != self.week_count:
            raise ValueError(f'La cantidad de semanas ({len(self.weeks)}) no coincide con week_count ({self.week_count})')
        
        return self

class SeasonUpdate(BaseModel):
    name: Optional[str] = None
    is_current: Optional[bool] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('El nombre no puede estar vacío')
            if len(v) > 100:
                raise ValueError('El nombre no puede exceder 100 caracteres')
            return v.strip()
        return v

class SeasonResponse(BaseModel):
    id: int
    name: str
    year: int
    week_count: int
    start_date: date
    end_date: date
    is_current: bool
    created_by: int
    weeks: List[WeekResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class LeagueSearchFilters(BaseModel):
    name: Optional[str] = Field(None, description="Búsqueda parcial por nombre de liga")
    season_id: Optional[int] = Field(None, description="Filtrar por temporada")
    status: Optional[Literal["pre_draft", "draft", "in_season", "completed"]] = Field(None, description="Filtrar por estado")
    

class LeagueSearchResult(BaseModel):
    id: int
    uuid: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str
    max_teams: int
    season_id: int
    season_name: str
    slots_available: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class JoinLeagueRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=12)
    user_alias: str = Field(..., min_length=1, max_length=50, description="Alias del usuario en esta liga")
    team_id: int = Field(..., ge=1, description="ID del equipo a usar en la liga")
    
    @field_validator("user_alias")
    @classmethod
    def validate_user_alias(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("El alias no puede estar vacío")
        if len(v) < 1 or len(v) > 50:
            raise ValueError("El alias debe tener entre 1 y 50 caracteres")
        return v


class JoinLeagueResponse(BaseModel):
    message: str
    league_id: int
    team_id: int
    user_alias: str
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

