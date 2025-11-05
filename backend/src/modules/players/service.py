from typing import Optional
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb, ensure_subdir, public_url, make_thumb_from_path
from ..teams.repository import get_by_id as get_team_by_id
from . import models, schemas, repository
import os
import uuid


def create_player(
    db: Session,
    *,
    payload: schemas.PlayerCreate,
    created_by: int,
    uploaded_file: Optional[object] = None
) -> models.Player:
    """
    Business logic for creating a player:
    - Validate required fields: name, position, team_id and image (either URL or file)
    - Enforce uniqueness of name per team (case-insensitive)
    - Handle image upload or URL and generate thumbnail
    - Create player record
    """
    name = payload.name.strip()
    position = payload.position  # already validated by Pydantic Literal
    team_id = payload.team_id

    if len(name) < 2:
        raise ValueError("Name must be at least 2 characters.")
    if not team_id:
        raise ValueError("Team is required.")

    # Validate team exists
    team = get_team_by_id(db, team_id)
    if not team:
        raise ValueError("Team not found.")

    # Uniqueness check within team
    existing = repository.get_by_name_ci_for_team(db, team_id=team_id, name=name)
    if existing:
        raise ValueError("A player with that name already exists in this team.")

    image_url: Optional[str] = None
    thumb_url: Optional[str] = None

    if uploaded_file:
        image_url, thumb_url = _save_player_upload(uploaded_file)
    elif payload.image_url:
        image_url = str(payload.image_url)
        thumb_url = try_download_and_thumb(image_url, subdir="players")
    else:
        # All fields must be filled, require an image one way or another
        raise ValueError("Image is required.")

    return repository.create_player(
        db,
        name=name,
        position=position,
        image_url=image_url,
        thumbnail_url=thumb_url,
        created_by=created_by,
        team_id=team_id,
    )


def _save_player_upload(upload_file) -> tuple[str, str]:
    players_dir = ensure_subdir("players")

    ext = os.path.splitext(upload_file.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"

    uid = uuid.uuid4().hex
    image_path = players_dir / f"{uid}{ext}"

    with open(image_path, "wb") as f:
        f.write(upload_file.file.read())
    upload_file.file.seek(0)

    thumb_path = make_thumb_from_path(image_path)

    return public_url(image_path), public_url(thumb_path)
