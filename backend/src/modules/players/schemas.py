from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Annotated, Optional, Literal
from datetime import datetime

# Valid positions
PositionType = Literal["QB", "RB", "WR", "TE", "K", "DST", "FLEX"]

class PlayerCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=128)]
    position: PositionType
    team_id: int
    image_url: Optional[str] = None

class Player(BaseModel):
    id: int
    name: str
    position: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    created_by: int
    team_id: int

    class Config:
        from_attributes = True


# Player news schemas
InjuryType = Literal['O', 'D', 'Q', 'P', 'FP', 'IR', 'PUP', 'SUS']


class PlayerNewsCreate(BaseModel):
    player_id: int
    summary: Annotated[str, Field(min_length=1, max_length=30)]
    text: Annotated[str, Field(min_length=10, max_length=300)]
    is_injury: bool = False
    injury_type: Optional[InjuryType] = None

    @field_validator('injury_type')
    def check_injury_required(cls, v, info):
        # If is_injury True then injury_type must be present
        data = info.data or {}
        if data.get('is_injury') and v is None:
            raise ValueError('injury_type is required when is_injury is true')
        return v


class PlayerNewsOut(BaseModel):
    id: int
    player_id: int
    author_id: int
    summary: str
    text: str
    is_injury: bool
    injury_type: Optional[str]
    changes: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
