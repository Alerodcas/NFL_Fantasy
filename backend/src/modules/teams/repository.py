from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from . import models

def get_by_id(db: Session, team_id: int) -> Optional[models.Team]:
    return db.get(models.Team, team_id)

def get_by_name_ci(db: Session, name: str) -> Optional[models.Team]:
    return db.execute(
        select(models.Team).where(func.lower(models.Team.name) == func.lower(name.strip()))
    ).scalar_one_or_none()

def create_team(
    db: Session,
    *,
    name: str,
    city: str,
    image_url: Optional[str],
    thumbnail_url: Optional[str],
    created_by: int,                 
) -> models.Team:
    team = models.Team(
        name=name.strip(),
        city=city.strip(),
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        is_active=True,
        created_by=created_by,     
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def update_team(
    db: Session,
    team: models.Team,
    *,
    name: Optional[str] = None,
    city: Optional[str] = None,
    image_url: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> models.Team:
    if name is not None:
        team.name = name.strip()
    if city is not None:
        team.city = city.strip()
    if image_url is not None:
        team.image_url = image_url
    if is_active is not None:
        team.is_active = is_active
    db.commit()
    db.refresh(team)
    return team

def list_teams(db: Session, q: Optional[str], active: Optional[bool]) -> List[models.Team]:
    stmt = select(models.Team)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((models.Team.name.ilike(like)) | (models.Team.city.ilike(like)))
    if active is not None:
        stmt = stmt.where(models.Team.is_active == active)
    stmt = stmt.order_by(models.Team.name.asc())
    return db.execute(stmt).scalars().all()
