from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from . import models


def get_by_id(db: Session, player_id: int) -> Optional[models.Player]:
    return db.get(models.Player, player_id)


def get_by_name_ci_for_team(db: Session, *, team_id: int, name: str) -> Optional[models.Player]:
    return db.execute(
        select(models.Player).where(
            models.Player.team_id == team_id,
            func.lower(models.Player.name) == func.lower(name)
        )
    ).scalar_one_or_none()


def create_player(
    db: Session,
    *,
    name: str,
    position: str,
    image_url: Optional[str],
    thumbnail_url: Optional[str],
    created_by: int,
    team_id: int,
) -> models.Player:
    player = models.Player(
        name=name,
        position=position,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        is_active=True,
        created_by=created_by,
        team_id=team_id,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player
