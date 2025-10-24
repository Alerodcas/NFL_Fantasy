from pydantic import BaseModel, Field, field_validator, validator
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

    team_name: str = Field(..., min_length=2, max_length=128)

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
    week_number: int = Field(..., ge=1, description="Número de semana")
    start_date: date
    end_date: date
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class WeekResponse(WeekCreate):
    id: int
    season_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SeasonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la temporada")
    week_count: int = Field(..., ge=1, le=52, description="Cantidad de semanas")
    start_date: date
    end_date: date
    is_current: bool = False
    weeks: List[WeekCreate] = []
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v
    
    @validator('start_date')
    def validate_start_date_not_past(cls, v):
        if v < date.today():
            raise ValueError('La fecha de inicio no puede estar en el pasado')
        return v
    
    @validator('weeks')
    def validate_weeks_count(cls, v, values):
        if 'week_count' in values and len(v) != values['week_count']:
            raise ValueError(f'Debe proporcionar exactamente {values["week_count"]} semanas')
        return v

class SeasonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_current: Optional[bool] = None

class SeasonResponse(BaseModel):
    id: int
    name: str
    year: int
    week_count: int
    start_date: date
    end_date: date
    is_current: bool
    created_by: int
    created_at: datetime
    weeks: List[WeekResponse] = []
    
    class Config:
        from_attributes = True
