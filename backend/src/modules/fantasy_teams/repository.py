from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models


def get_by_id(db: Session, ft_id: int) -> Optional[models.FantasyTeam]:
    return db.get(models.FantasyTeam, ft_id)


def get_by_name_in_league_ci(db: Session, *, league_id: int, name: str) -> Optional[models.FantasyTeam]:
    return db.execute(
        select(models.FantasyTeam).where(
            models.FantasyTeam.league_id == league_id,
            func.lower(models.FantasyTeam.name) == func.lower(name.strip()),
        )
    ).scalar_one_or_none()


def list_by_league(db: Session, league_id: int) -> List[models.FantasyTeam]:
    stmt = (
        select(models.FantasyTeam)
        .where(models.FantasyTeam.league_id == league_id)
        .order_by(models.FantasyTeam.created_at.desc())
    )
    return db.execute(stmt).scalars().all()


def create_fantasy_team(
    db: Session,
    *,
    name: str,
    image_url: Optional[str],
    thumbnail_url: Optional[str],
    user_id: int,
    league_id: int,
) -> models.FantasyTeam:
    team = models.FantasyTeam(
        name=name,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        is_active=True,
        user_id=user_id,
        league_id=league_id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team
