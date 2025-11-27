from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import status
from werkzeug.utils import secure_filename
import os
import json
import shutil
from sqlalchemy.orm import Session

from ...config.database import get_db
from ..users.router import get_current_user
from .schemas import Player as PlayerOut, PlayerCreate
from .schemas import PlayerNewsCreate, PlayerNewsOut
from . import service, validators, repository
from ..media import repository as media_repo

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
    # Validate payload before calling service
    try:
        validated = validators.validate_single_player(db=db, payload=payload.dict())
    except ValueError as ve:
        error_msg = str(ve)
        low = error_msg.lower()
        if "already exists" in low or "ya existe" in low:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)

    try:
        # Build validated payload and create
        validated_payload = PlayerCreate(**validated)
        player = service.create_player(db=db, payload=validated_payload, created_by=current_user.id)
        try:
            db.commit()
            db.refresh(player)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error saving player")

        return player
    except ValueError as ve:
        error_msg = str(ve)
        low = error_msg.lower()
        if "already exists" in low or "ya existe" in low:
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
        # Validate using validators with the uploaded file
        try:
            validated = validators.validate_single_player(db=db, payload=payload.dict(), uploaded_file=image)
        except ValueError as ve:
            error_msg = str(ve)
            low = error_msg.lower()
            if "already exists" in low or "ya existe" in low:
                raise HTTPException(status_code=409, detail=error_msg)
            raise HTTPException(status_code=422, detail=error_msg)

        # Persist the uploaded image using the media repository (persistence layer)
        try:
            image_url, thumb_url = media_repo.save_player_upload(image)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error saving uploaded image: " + str(e))

        # Build payload including the saved image URL and create the player
        validated_payload = PlayerCreate(**{**validated, "image_url": image_url})
        player = service.create_player(db=db, payload=validated_payload, created_by=current_user.id, thumbnail_url=thumb_url)
        try:
            db.commit()
            db.refresh(player)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error saving player")

        return player
    except HTTPException:
        # Re-raise HTTP errors so FastAPI can return the intended response body
        raise
    except ValueError as ve:
        error_msg = str(ve)
        low = error_msg.lower()
        if "already exists" in low or "ya existe" in low:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=422, detail=error_msg)
    except Exception as e:
        # Unexpected error; return a helpful message while logging the exception
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Invalid image file.")
    

@router.post("/batch-upload", status_code=200)
def batch_upload_players(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)

    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Se requiere un archivo JSON")

    try:
        result = service.process_players_batch(
            db=db,
            file=file.file,           
            created_by=current_user.id
        )
        return {
            "message": f"{len(result['created'])} jugadores creados correctamente.",
            "created": result["created"],
        }

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno: " + str(e))



@router.get("", response_model=list[PlayerOut])
def list_players(
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    # If team_id provided, return players for that team
    if team_id is not None:
        players = repository.list_players_by_team(db=db, team_id=team_id)
        return players
    # Otherwise, return empty list (or could later support global list)
    return []



@router.post("/{player_id}/news", response_model=PlayerNewsOut, status_code=status.HTTP_201_CREATED)
def create_player_news(
    player_id: int,
    payload: PlayerNewsCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    _require_admin(current_user)

    # Ensure path player_id overrides any body value
    payload = PlayerNewsCreate(**{**payload.dict(), "player_id": player_id})

    try:
        news = service.create_player_news(db=db, payload=payload, author_id=current_user.id)
        try:
            db.commit()
            db.refresh(news)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error saving news")

        return news

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))


@router.get("/{player_id}/news", response_model=list[PlayerNewsOut], status_code=200)
def list_player_news(
    player_id: int,
    db: Session = Depends(get_db),
):
    news = service.list_news_for_player(db=db, player_id=player_id)
    return news



@router.get("/{player_id}", response_model=PlayerOut, status_code=200)
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
):
    player = repository.get_by_id(db=db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
