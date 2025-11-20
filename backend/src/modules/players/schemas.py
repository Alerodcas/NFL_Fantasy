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
