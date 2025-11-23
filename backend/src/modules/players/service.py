from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb, save_upload_file, save_processed_copy, public_url
from ...config.paths import PATH_PLAYERS, PATH_PLAYERS_PROCESSED
from ..teams.repository import get_by_id as get_team_by_id
from . import models, schemas, repository, validators
import os
import uuid
 
import os
from pathlib import Path
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from contextlib import nullcontext


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

    # Assumes payload has already been validated by caller/validators.

    # Process image (if provided). Service does not perform validation of payload.
    if uploaded_file:
        image_url, thumb_url = _save_player_upload(uploaded_file)
    else:
        image_url = payload.image_url
        thumb_url = try_download_and_thumb(image_url, subdir=PATH_PLAYERS) if image_url else None

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
    # Delegate actual file saving and thumbnail generation to core.media
    return save_upload_file(upload_file, PATH_PLAYERS)




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

    # Intentar leer JSON (leer el contenido en memoria para poder guardar una copia procesada)
    try:
        raw_content = file.read()
        if isinstance(raw_content, bytes):
            text_content = raw_content.decode("utf-8")
        else:
            text_content = raw_content
        data = json.loads(text_content)
    except Exception:
        raise ValueError("Malformed JSON or unreadable file")

    # Debe ser un array
    if not isinstance(data, list):
        raise ValueError("JSON must contain an array of players")

    errors = []
    validated_items = []
    created = []
    seen_items = []

    # Delegate all validation to validators.validate_players_batch
    validated_items = validators.validate_players_batch(db=db, data=data)



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

        # Save a timestamped copy of the processed file via core.media
        try:
            save_processed_copy(raw_content, PATH_PLAYERS_PROCESSED, prefix="batch")
        except Exception:
            # Do not fail the operation if saving the copy fails
            pass

        return {"created": created}

    except (IntegrityError, ValueError) as e:
        db.rollback()
        raise ValueError(f"Error creating players: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error during batch creation: {str(e)}")
