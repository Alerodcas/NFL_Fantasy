from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb, ensure_subdir, public_url, make_thumb_from_path
from ..teams.repository import get_by_id as get_team_by_id, get_by_name_ci
from . import models, schemas, repository
import os
import uuid
from .repository import get_by_name_ci_for_team
import os
from pathlib import Path
import json
from sqlalchemy.exc import IntegrityError
from contextlib import nullcontext


ALLOWED_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DST", "FLEX"}


def create_player(
    db: Session,
    *,
    payload: schemas.PlayerCreate,
    created_by: int,
    uploaded_file: Optional[object] = None
) -> models.Player:

    name = payload.name.strip()
    position = payload.position
    team_id = payload.team_id

    # Validación mínima: TODO ya debería venir validado
    if not name or not team_id:
        raise ValueError("Missing required data to create player")

    # Procesar imagen sin escribir nada en DB todavía
    if uploaded_file:
        image_url, thumb_url = _save_player_upload(uploaded_file)
    else:
        image_url = payload.image_url
        if not image_url:
            raise ValueError("Image is required.")
        thumb_url = try_download_and_thumb(image_url, subdir="players")

    player = models.Player(
        name=name,
        position=position,
        image_url=image_url,
        thumbnail_url=thumb_url,
        is_active=True,
        created_by=created_by,
        team_id=team_id,
    )

    # Solo add → ni commit, ni flush aquí
    db.add(player)
    return player




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


def _validate_item_json(item: dict, idx: int, seen_items: list):
    # Lista de errores encontrados en esta fila
    errors = []

    # Validar campo name
    if "name" not in item or not isinstance(item["name"], str) or not item["name"].strip():
        errors.append(f"Row {idx}: missing field 'name'")
    name = item.get("name", "").strip()

    # Validar posición permitida
    pos = item.get("position")
    if not pos or not isinstance(pos, str) or not pos.strip():
        errors.append(f"Row {idx}: missing field 'position'")
    else:
        pos_up = pos.strip().upper()
        if pos_up not in ALLOWED_POSITIONS:
            allowed = ", ".join(sorted(ALLOWED_POSITIONS))
            errors.append(
                f"Row {idx}: invalid position '{pos}'. Allowed values: {allowed}"
            )

    # Validar nombre del equipo
    if "team" not in item or not item["team"].strip():
        errors.append(f"Row {idx}: missing field 'team'")
    team = item.get("team", "").strip()

    # Validar imagen
    if "image" not in item or not item["image"]:
        errors.append(f"Row {idx}: missing field 'image'")
    image = item.get("image")

    # Validar duplicados en el archivo JSON
    if not errors:
        for prev in seen_items:
            # Mismo nombre + equipo
            if prev["name"].lower() == name.lower() and prev["team"].lower() == team.lower():
                errors.append(
                    f"Row {idx}: player '{name}' is duplicated inside the file for team '{team}'"
                )
                break
            # Mismo ID (si incluyen id)
            if item.get("id") and prev.get("id") and item["id"] == prev["id"]:
                errors.append(
                    f"Row {idx}: ID '{item['id']}' is duplicated inside the file"
                )
                break

    # Registrar solo si pasó todas las validaciones
    if not errors:
        seen_items.append({
            "name": name,
            "team": team,
            "id": item.get("id")
        })

    return errors



def validate_player_db(
    db: Session,
    *,
    name: str,
    team_id: Optional[int],
    image_url: Optional[str],
    index: int
) -> list[str]:
    errors = []

    # Nombre mínimo
    if len(name) < 2:
        errors.append(f"Row {index}: Name must be at least 2 characters.")

    # Validar que haya equipo
    if not team_id:
        errors.append(f"Row {index}: Team not found.")
        return errors

    # Validar unicidad en la base de datos
    existing = repository.get_by_name_ci_for_team(db, team_id=team_id, name=name)
    if existing:
        errors.append(f"Row {index}: A player with that name already exists in this team.")

    # Validar que exista imagen
    if not image_url:
        errors.append(f"Row {index}: Image is required.")

    return errors



def _process_image_from_url(image_url: str, subdir: str = "players") -> Tuple[str, str]:
    """
    Intenta descargar y generar thumbnail usando core.media utilities.
    Devuelve (image_public_url, thumb_public_url)
    """
    thumb = try_download_and_thumb(image_url, subdir=subdir)
    # try_download_and_thumb devuelve thumb url; asumimos la URL pública de la imagen es la misma pasada.
    # En caso de querer guardar la original en media también, implementá descarga explícita.
    return image_url, thumb

def process_players_batch(db: Session, *, file, created_by: int):

    # Intentar leer JSON
    try:
        data = json.load(file)
    except Exception:
        raise ValueError("Malformed JSON or unreadable file")

    # Debe ser un array
    if not isinstance(data, list):
        raise ValueError("JSON must contain an array of players")

    errors = []
    validated_items = []
    created = []
    seen_items = []

    # Validar fila por fila ANTES de tocar la base
    for idx, item in enumerate(data, start=1):
        
        item_errors = _validate_item_json(item, idx, seen_items)
        if item_errors:
            errors.extend(item_errors)
            continue

        name = item["name"].strip()
        position = item["position"].strip().upper()
        image_url = item.get("image")
        team_name = item.get("team").strip()

        # Obtener ID del equipo desde DB
        team = get_by_name_ci(db, team_name)
        team_id = team.id if team else None

        # Validación con DB
        db_errors = validate_player_db(
            db=db,
            name=name,
            team_id=team_id,
            image_url=image_url,
            index=idx
        )
        if db_errors:
            errors.extend(db_errors)
            continue

        validated_items.append({
            "name": name,
            "position": position,
            "team_id": team_id,
            "image_url": image_url
        })

    # Si hay cualquier error → abortar todo
    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(errors))

    # Crear todos los jugadores en una sola transacción
    try:
        for item in validated_items:
            payload = schemas.PlayerCreate(**item)

            player = create_player(
                db,
                payload=payload,
                created_by=created_by
            )
            created.append(player.name)

        db.commit()
        return {"created": created}

    except (IntegrityError, ValueError) as e:
        db.rollback()
        raise ValueError(f"Error creating players: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error during batch creation: {str(e)}")
