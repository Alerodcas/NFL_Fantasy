from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ..users.router import get_current_user
from .repository import get_by_id
from .schemas import Team as TeamOut, TeamCreate, TeamUpdate
from . import service

router = APIRouter()

def _require_admin(user) -> None:
    if getattr(user, "role", None) not in ("admin", "manager", "owner"):
        # keep your permission model flexible; require at least "manager"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

# ---------- Endpoints ----------

# A) Create team via JSON (name, city, image_url)
@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team_json(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)
    try:
        team = service.create_team(db=db, payload=payload, created_by=current_user.id)
        return team
    except ValueError as ve:
        error_msg = str(ve)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)

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
    
    try:
        payload = TeamCreate(name=name, city=city, image_url=None)
        team = service.create_team(db=db, payload=payload, created_by=current_user.id, uploaded_file=image)
        return team
    except ValueError as ve:
        error_msg = str(ve)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

# C) List
@router.get("", response_model=List[TeamOut])
def list_teams(
    q: Optional[str] = None,
    active: Optional[bool] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return service.list_teams(db=db, q=q, active=active, user_id=user_id)

# D) Get by id
@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = service.get_team_by_id(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")
    return team

# E) Update (partial)
@router.put("/{team_id}", response_model=TeamOut)
def update_team_endpoint(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    _require_admin(current_user)
    team = get_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")

    try:
        updated = service.update_team(db=db, team=team, payload=payload)
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=409, detail=str(ve))
