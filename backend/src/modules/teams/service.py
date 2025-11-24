from typing import Optional, List
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb
from ...config.paths import PATH_TEAMS
from . import models, schemas, repository
import os
import uuid
from pathlib import Path


def create_team(
    db: Session,
    *,
    payload: schemas.TeamCreate,
    created_by: int,
) -> models.Team:
    """
    Business logic for creating a team:
    - Validate name and city length
    - Check uniqueness of name (case-insensitive)
    - Handle image URL or uploaded file
    - Generate thumbnail
    - Create team record
    
    If uploaded_file is provided, it should be a FastAPI UploadFile.
    """
    name = payload.name.strip()
    city = payload.city.strip()
    
    # Validation
    if len(name) < 2 or len(city) < 2:
        raise ValueError("Name and city must be at least 2 characters.")
    
    # Uniqueness check
    existing = repository.get_by_name_ci(db, name)
    if existing:
        raise ValueError("A team with that name already exists.")
    
    # Handle image: router is responsible for persisting uploads and passing `image_url`.
    image_url = None
    thumb_url = None
    if payload.image_url:
        image_url = str(payload.image_url)
        thumb_url = try_download_and_thumb(image_url, subdir=PATH_TEAMS)
    
    return repository.create_team(
        db,
        name=name,
        city=city,
        image_url=image_url,
        thumbnail_url=thumb_url,
        created_by=created_by
    )


def update_team(
    db: Session,
    team: models.Team,
    *,
    payload: schemas.TeamUpdate
) -> models.Team:
    """
    Business logic for updating a team:
    - Validate name uniqueness if changed
    - Update fields
    """
    # Guard uniqueness on name change
    if payload.name:
        other = repository.get_by_name_ci(db, payload.name)
        if other and other.id != team.id:
            raise ValueError("A team with that name already exists.")
    
    return repository.update_team(
        db,
        team,
        name=payload.name,
        city=payload.city,
        image_url=str(payload.image_url) if payload.image_url else None,
        is_active=payload.is_active
    )


def list_teams(
    db: Session,
    *,
    query: Optional[str] = None,
    active_only: Optional[bool] = None,
    user_id: Optional[int] = None
) -> List[models.Team]:
    """
    List teams with optional filters.
    """
    return repository.list_teams(db, q=query, active=active_only, user_id=user_id)


def get_team_by_id(db: Session, team_id: int) -> Optional[models.Team]:
    """
    Retrieve a single team by ID.
    """
    return repository.get_by_id(db, team_id)


def _save_team_upload(upload_file) -> tuple[str, str]:
    """
    Save uploaded file and generate thumbnail.
    Returns (image_url, thumbnail_url).
    """
    # Deprecated: routers should persist uploads via modules.media.repository
    raise RuntimeError("_save_team_upload is deprecated; persist uploads via modules.media.repository from the router")
