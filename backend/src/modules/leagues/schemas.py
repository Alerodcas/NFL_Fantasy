from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

_ALLOWED_TEAM_SIZES = {4, 6, 8, 10, 12, 14, 16, 18, 20}

class LeagueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    max_teams: int
    password: str = Field(..., min_length=8, max_length=12)
    playoff_format: Literal[4, 6]
    allow_decimal_scoring: bool = True

    # Commissioner team data (user story: must enter team name upon creation)
    team_name: str = Field(..., min_length=2)
    team_city: Optional[str] = Field(None, min_length=2)  # teams.city is NOT NULL; we’ll default to 'N/A' if None

    @field_validator("max_teams")
    @classmethod
    def check_team_sizes(cls, v: int):
        if v not in _ALLOWED_TEAM_SIZES:
            raise ValueError(f"max_teams must be one of {_ALLOWED_TEAM_SIZES}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        # 8–12 chars, alphanumeric, at least one lowercase and one uppercase
        import re
        if not re.fullmatch(r"(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9]{8,12}", v):
            raise ValueError("Password must be 8–12 chars, alphanumeric, include at least one lowercase and one uppercase.")
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

