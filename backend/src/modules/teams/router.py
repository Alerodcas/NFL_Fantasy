import os
from pathlib import Path
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...core.media import ensure_subdir, public_url, make_thumb_from_path, try_download_and_thumb
from ..users.router import get_current_user
from .repository import (
    get_by_id, get_by_name_ci, create_team as repo_create, list_teams as repo_list, update_team as repo_update
)
from .schemas import Team as TeamOut, TeamCreate, TeamUpdate

router = APIRouter()

# Ensure media directory for teams
TEAM_DIR = ensure_subdir("teams")

def _require_admin(user) -> None:
    if getattr(user, "role", None) not in ("admin", "manager", "owner"):
        # keep your permission model flexible; require at least "manager"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

def _save_upload(upload: UploadFile) -> tuple[str, str]:
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"
    uid = uuid.uuid4().hex
    image_path = TEAM_DIR / f"{uid}{ext}"

    with open(image_path, "wb") as f:
        f.write(upload.file.read())
    upload.file.seek(0)
    # Create an actual thumbnail image next to the uploaded image
    thumb_path = make_thumb_from_path(image_path)
    return public_url(image_path), public_url(thumb_path)

# ---------- Endpoints ----------

# A) Create team via JSON (name, city, image_url)
@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team_json(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)

    name = payload.name.strip()
    city = payload.city.strip()
    if len(name) < 2 or len(city) < 2:
        raise HTTPException(status_code=422, detail="Name and city must be at least 2 characters.")

    if get_by_name_ci(db, name):
        raise HTTPException(status_code=409, detail="A team with that name already exists.")

    thumb_url = None
    img_url = payload.image_url if payload.image_url else None
    # Try to generate a local thumbnail when a URL is provided
    if img_url:
        thumb_url = try_download_and_thumb(str(img_url), subdir="teams")

    team = repo_create(db, name=name, city=city, image_url=str(img_url) if img_url else None, thumbnail_url=thumb_url, created_by=current_user.id,
)
    return team

# B) Create team via file upload (optional alternative)
@router.post("/upload", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team_upload(
    name: str = Form(...),
    city: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)
    name_clean = name.strip()
    city_clean = city.strip()

    if len(name_clean) < 2 or len(city_clean) < 2:
        raise HTTPException(status_code=422, detail="Name and city must be at least 2 characters.")

    if get_by_name_ci(db, name_clean):
        raise HTTPException(status_code=409, detail="A team with that name already exists.")

    try:
        image_url, thumb_url = _save_upload(image)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    team = repo_create(db, name=name_clean, city=city_clean, image_url=image_url, thumbnail_url=thumb_url,         created_by=current_user.id,)
    return team

# C) List
@router.get("", response_model=List[TeamOut])
def list_teams(
    q: Optional[str] = None,
    active: Optional[bool] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return repo_list(db, q, active, user_id)

# D) Get by id
@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = get_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    return team

# E) Update (partial)
@router.put("/{team_id}", response_model=TeamOut)
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    _require_admin(current_user)
    team = get_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")

    # Guard uniqueness on name change
    if payload.name:
        other = get_by_name_ci(db, payload.name)
        if other and other.id != team.id:
            raise HTTPException(status_code=409, detail="A team with that name already exists.")

    updated = repo_update(
        db,
        team,
        name=payload.name,
        city=payload.city,
        image_url=str(payload.image_url) if payload.image_url else None,
        is_active=payload.is_active,
    )
    return updated
