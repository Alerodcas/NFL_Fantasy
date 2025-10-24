from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date, datetime
from typing import List, Optional


class WeekBase(BaseModel):
    week_number: int = Field(..., ge=1, description="Week number (1-based)")
    start_date: date
    end_date: date


class WeekCreate(WeekBase):
    pass


class Week(WeekBase):
    id: int
    season_id: int

    class Config:
        from_attributes = True


class SeasonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    is_current: bool = False


class SeasonCreate(BaseModel):
    name: str
    year: int
    start_date: date
    end_date: date
    description: Optional[str] = None
    num_weeks: int
    is_current: bool = False

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('name must not be empty')
        return v

    @field_validator('num_weeks')
    def num_weeks_range(cls, v: int) -> int:
        if v < 1 or v > 52:
            raise ValueError('num_weeks must be between 1 and 52')
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        
        # Validate dates are not in the past
        today = date.today()
        if self.start_date < today:
            raise ValueError('Start date cannot be in the past')
        if self.end_date < today:
            raise ValueError('End date cannot be in the past')
        
        return self


class SeasonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        return v.strip() if v else None


class SeasonCreated(BaseModel):
    id: int
    created_at: datetime
    weeks: List[Week] = []

    class Config:
        from_attributes = True
