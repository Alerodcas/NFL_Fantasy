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


def _validate_item(item: Dict[str, Any], index: int) -> List[str]:
    """Valida un jugador individual, devuelve lista de errores (vacía si ok)."""
    errs = []
    required = ["id", "name", "position", "team", "image"]

    # Validar campos requeridos
    for f in required:
        if f not in item or item[f] in (None, ""):
            errs.append(f"Fila {index}: falta campo '{f}'")

    # Nombre mínimo
    if "name" in item and isinstance(item["name"], str) and len(item["name"].strip()) < 2:
        errs.append(f"Fila {index}: nombre muy corto")

    # Validar posición permitida
    valid_positions = {"QB", "RB", "WR", "TE", "K", "DEF"}
    if "position" in item:
        pos = str(item["position"]).strip().upper()
        if pos not in valid_positions:
            errs.append(
                f"Fila {index}: posición inválida '{item['position']}', debe ser una de {', '.join(valid_positions)}"
            )

    return errs

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
    import json

    try:
        data = json.load(file)
    except Exception:
        raise ValueError("JSON malformado o ilegible")

    if not isinstance(data, list):
        raise ValueError("El JSON debe contener un array de jugadores")

    errors = []
    normalized_items = []

    for idx, item in enumerate(data, start=1):
        item_errors = _validate_item(item, idx)
        if item_errors:
            errors.extend(item_errors)
            continue

        team_name = item.get("team")
        if not team_name:
            errors.append(f"Fila {idx}: falta campo 'team'")
            continue

        team = get_by_name_ci(db, team_name.strip())
        if not team:
            errors.append(f"Fila {idx}: equipo '{team_name}' no existe")
            continue

        existing = get_by_name_ci_for_team(db, name=item["name"], team_id=team.id)
        if existing:
            errors.append(f"Fila {idx}: '{item['name']}' ya existe en equipo '{team_name}'")
            continue

        normalized_items.append({
            "id": item.get("id"),
            "name": item["name"].strip(),
            "position": item["position"].strip().upper(),
            "team_id": team.id,
            "image": item["image"],
        })

    if errors:
        raise ValueError("Errores de validación:\n" + "\n".join(errors))

    # Si pasó validación, crear en DB
    created = []

    try:
        for item in normalized_items:
            thumb_url = try_download_and_thumb(item["image"], subdir="players")

            player = models.Player(
                id=int(item["id"]) if item.get("id") else None,
                name=item["name"],
                position=item["position"],
                team_id=item["team_id"],
                image_url=item["image"],
                thumbnail_url=thumb_url,
                is_active=True,
                created_by=created_by
            )
            db.add(player)
            created.append(item["name"])

        db.commit()
        return {"created": created}

    except Exception:
        db.rollback()
        raise

