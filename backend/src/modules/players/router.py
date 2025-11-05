from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import status
from sqlalchemy.orm import Session

from ...config.database import get_db
from ..users.router import get_current_user
from .schemas import Player as PlayerOut, PlayerCreate
from . import service

router = APIRouter()


def _require_admin(user) -> None:
    if getattr(user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")


@router.post("", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player_json(
    payload: PlayerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)
    # Enforce all fields filled for JSON route: require image_url present
    if not payload.image_url:
        raise HTTPException(status_code=422, detail="image_url is required for JSON payload")
    try:
        player = service.create_player(db=db, payload=payload, created_by=current_user.id)
        return player
    except ValueError as ve:
        error_msg = str(ve)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)


@router.post("/upload", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player_upload(
    name: str = Form(...),
    position: str = Form(...),
    team_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)

    try:
        payload = PlayerCreate(name=name, position=position, team_id=team_id, image_url=None)
        player = service.create_player(db=db, payload=payload, created_by=current_user.id, uploaded_file=image)
        return player
    except ValueError as ve:
        error_msg = str(ve)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")
