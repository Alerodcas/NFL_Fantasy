import os
from pathlib import Path
import uuid
from typing import Optional, List
from PIL import Image
import requests

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ..users.router import get_current_user
from .repository import (
    get_by_id, get_by_name_ci, create_team as repo_create, list_teams as repo_list, update_team as repo_update
)
from .schemas import Team as TeamOut, TeamCreate, TeamUpdate

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]      # backend/src
MEDIA_ROOT = BASE_DIR / "media"
TEAM_DIR = MEDIA_ROOT / "teams"
TEAM_DIR.mkdir(parents=True, exist_ok=True)
THUMB_SIZE = (256, 256)

def _require_admin(user) -> None:
    if getattr(user, "role", None) not in ("admin", "manager", "owner"):
        # keep your permission model flexible; require at least "manager"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

def _public_url(fs_path: Path) -> str:
    rel = fs_path.relative_to(MEDIA_ROOT).as_posix()
    return f"/media/{rel}"

def _make_thumb_from_path(image_path: str) -> str:
    thumb_path = os.path.splitext(image_path)[0] + "_thumb.png"
    with Image.open(image_path) as im:
        im = im.convert("RGB")
        im.thumbnail(THUMB_SIZE, Image.LANCZOS)
        canvas = Image.new("RGB", THUMB_SIZE, (255, 255, 255))
        x = (THUMB_SIZE[0] - im.width) // 2
        y = (THUMB_SIZE[1] - im.height) // 2
        canvas.paste(im, (x, y))
        canvas.save(thumb_path, format="PNG")
    return thumb_path

def _save_upload(upload: UploadFile) -> (str, str):
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"
    uid = uuid.uuid4().hex
    image_path = TEAM_DIR / f"{uid}{ext}"

    with open(image_path, "wb") as f:
        f.write(upload.file.read())
    upload.file.seek(0)
    thumb_path = TEAM_DIR / f"{uid}_thumb.png"
    return _public_url(image_path), _public_url(thumb_path)

def _try_download_and_thumb(image_url: str) -> Optional[str]:
    """
    Try to download 'image_url' to local media to generate a thumbnail.
    If download fails, return None (we'll still store the URL provided).
    """
    try:
        uid = uuid.uuid4().hex
        ext = os.path.splitext(image_url)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            ext = ".png"
        image_path = TEAM_DIR / f"{uid}{ext}"

        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
        with open(image_path, "wb") as f:
            f.write(r.content)

        thumb_path = TEAM_DIR / f"{uid}_thumb.png"
        return _public_url(thumb_path)
    except Exception:
        return None

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
        thumb_url = _try_download_and_thumb(str(img_url))

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
