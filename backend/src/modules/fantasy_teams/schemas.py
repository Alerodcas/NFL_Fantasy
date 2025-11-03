from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Optional
from datetime import datetime

class FantasyTeamCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=128)]
    image_url: Optional[HttpUrl] = None

class FantasyTeam(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    user_id: int
    league_id: int

    class Config:
        from_attributes = True
