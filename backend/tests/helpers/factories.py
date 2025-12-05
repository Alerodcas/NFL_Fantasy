from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from modules.users import models as user_models
from modules.teams import models as team_models
from modules.fantasy_teams import models as fantasy_models
from modules.leagues import models as league_models
from modules.players import models as player_models


def create_user(db: Session, *, name: str = "User", email: str = "u@example.com", alias: str = "u", hashed_password: str = "x") -> user_models.User:
    u = user_models.User(name=name, email=email, alias=alias, hashed_password=hashed_password)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_team(db: Session, *, created_by: int, name: str = "TeamX", city: str = "City") -> team_models.Team:
    t = team_models.Team(name=name, city=city, created_by=created_by)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def create_fantasy_team(db: Session, *, user_id: int, league_id: int, name: str = "FT") -> fantasy_models.FantasyTeam:
    ft = fantasy_models.FantasyTeam(name=name, image_url=None, thumbnail_url=None, is_active=True, user_id=user_id, league_id=league_id)
    db.add(ft)
    db.commit()
    db.refresh(ft)
    return ft


def create_season(db: Session, *, name: str, year: int, created_by: int, start_date, end_date, week_count: int = 10, is_current: bool = False) -> league_models.Season:
    s = league_models.Season(name=name, year=year, week_count=week_count, start_date=start_date, end_date=end_date, is_current=is_current, created_by=created_by, cached_weeks=[])
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def create_league(db: Session, *, name: str, created_by: int, season_id: int, max_teams: int = 8, playoff_format: int = 4) -> league_models.League:
    lg = league_models.League(name=name, description=None, max_teams=max_teams, password_hash="x", playoff_format=playoff_format, created_by=created_by, season_id=season_id, roster_schema={}, scoring_schema={})
    db.add(lg)
    db.commit()
    db.refresh(lg)
    return lg


def create_player(db: Session, *, name: str, position: str, created_by: int, team_id: int, image_url: Optional[str] = None) -> player_models.Player:
    p = player_models.Player(name=name, position=position, image_url=image_url, thumbnail_url=None, is_active=True, created_by=created_by, team_id=team_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_player_news(db: Session, *, player_id: int, author_id: int, summary: str, text: str, is_injury: bool = False, injury_type: Optional[str] = None):
    n = player_models.PlayerNews(player_id=player_id, author_id=author_id, summary=summary, text=text, is_injury=is_injury, injury_type=injury_type, changes=None)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n
