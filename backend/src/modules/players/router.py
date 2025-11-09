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
    

@router.post("/batch-upload", status_code=200)
def batch_upload_players(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Solo admins
    _require_admin(current_user)

    # Validaciones de archivo
    filename = secure_filename(file.filename or "")
    if not filename or not filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Se requiere un archivo .json")

    # Rutas de almacenamiento (usar MEDIA_DIR relative a project)
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parents[3]  # ajusta si es necesario
    incoming_dir = BASE_DIR / "media" / "players" / "incoming"
    processed_dir = BASE_DIR / "media" / "players" / "processed"
    incoming_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    incoming_path = incoming_dir / filename

    # Guardar temporalmente el archivo
    with open(incoming_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Procesar usando la capa de servicio
    try:
        result = service.process_players_batch(
            db=db,
            file_path=str(incoming_path),
            created_by=current_user.id,
        )

        # mover archivo a processed con sufijo __processed.json
        processed_name = filename.replace(".json", f"__processed.json")
        (processed_dir / processed_name).unlink(missing_ok=True)  # por si existe
        shutil.move(str(incoming_path), str(processed_dir / processed_name))

        return {
            "message": f"{len(result['created'])} jugadores creados correctamente.",
            "created": result["created"],
            "errors": result["errors"],
        }
    except ValueError as ve:
        # errores de validación (no crea nada)
        # borrar archivo incoming o mover a processed con sufijo __failed.json si querés
        failed_name = filename.replace(".json", f"__failed.json")
        shutil.move(str(incoming_path), str(processed_dir / failed_name))
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # error inesperado
        if incoming_path.exists():
            incoming_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
