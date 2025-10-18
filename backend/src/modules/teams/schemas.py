from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Optional
from datetime import datetime

# Payload when creating from a FORM *or* JSON with a URL
# (thumbnail is generated server-side)
class TeamCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=128)]
    city: Annotated[str, Field(min_length=2, max_length=128)]
    image_url: Optional[HttpUrl] = None  # if provided, we can store it and try to thumbnail it later

# Partial update
class TeamUpdate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=128)] | None = None
    city: Annotated[str, Field(min_length=2, max_length=128)] | None = None
    image_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

# Response model
class Team(BaseModel):
    id: int
    name: str
    city: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True
