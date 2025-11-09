from typing import Optional, List
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb, ensure_subdir, public_url, make_thumb_from_path
from . import models, schemas, repository
import os
import uuid
from pathlib import Path


def create_team(
    db: Session,
    *,
    payload: schemas.TeamCreate,
    created_by: int,
    uploaded_file: Optional[object] = None
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
    
    # Handle image
    image_url = None
    thumb_url = None
    
    if uploaded_file:
        # File upload path
        image_url, thumb_url = _save_team_upload(uploaded_file)
    elif payload.image_url:
        # URL-based image
        image_url = str(payload.image_url)
        thumb_url = try_download_and_thumb(image_url, subdir="teams")
    
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
    team_dir = ensure_subdir("teams")
    
    ext = os.path.splitext(upload_file.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"
    
    uid = uuid.uuid4().hex
    image_path = team_dir / f"{uid}{ext}"
    
    with open(image_path, "wb") as f:
        f.write(upload_file.file.read())
    upload_file.file.seek(0)
    
    # Generate thumbnail
    thumb_path = make_thumb_from_path(image_path)
    
    return public_url(image_path), public_url(thumb_path)
