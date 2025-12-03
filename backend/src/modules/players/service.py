from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ...core.media import try_download_and_thumb, save_processed_copy, public_url
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
    thumbnail_url: Optional[str] = None
) -> models.Player:

    name = payload.name.strip()
    position = payload.position
    team_id = payload.team_id

    # Assumes payload has already been validated by caller/validators.

    # Service no longer performs filesystem image persistence.
    # The caller (router or repository) must provide `payload.image_url` and optionally `thumbnail_url`.
    image_url = payload.image_url
    thumb_url = thumbnail_url if thumbnail_url is not None else (try_download_and_thumb(image_url, subdir=PATH_PLAYERS) if image_url else None)

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
    # Deprecated: persistence moved to `modules.media.repository.save_player_upload`
    raise RuntimeError("_save_player_upload is deprecated; use modules.media.repository.save_player_upload from router")




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


def create_player_news(db: Session, *, payload: schemas.PlayerNewsCreate, author_id: int) -> models.PlayerNews:
    """Create a PlayerNews instance (does not commit). Validates player existence and activity."""
    # Validate DB-level requirements
    try:
        validated = validators.validate_player_news(db=db, payload=payload.dict())
    except ValueError as ve:
        raise ve

    # Capture previous designation for 'changes' audit
    player = repository.get_by_id(db=db, player_id=validated['player_id'])
    prev_designation = None
    if player is not None:
        prev_designation = getattr(player, 'visible_designation', None)

    news = models.PlayerNews(
        player_id=validated['player_id'],
        author_id=author_id,
        summary=validated['summary'].strip(),
        text=validated['text'].strip(),
        is_injury=validated.get('is_injury', False),
        injury_type=validated.get('injury_type'),
        changes=(validated.get('changes') if validated.get('changes') is not None else (
            {'prev_designation': prev_designation, 'new_designation': (validated.get('injury_type') if validated.get('is_injury') else None)} if validated.get('update_state') else None
        )),
    )

    # add to session but don't commit here (router will commit)
    db.add(news)

    # Update player's visible designation & timestamp based on this news only if requested
    try:
        if player and validated.get('update_state'):
            player_visible = news.injury_type if news.is_injury else None
            player.visible_designation = player_visible
            # Use server-side timestamp on commit; also set a client-side timestamp for immediate readback
            from datetime import datetime
            player.visible_designation_updated_at = datetime.utcnow()
    except Exception:
        # Do not fail creation if we can't update player visible fields; leave unhandled
        pass

    return news


def list_news_for_player(db: Session, *, player_id: int, limit: int = 50):
    return repository.list_news_for_player(db=db, player_id=player_id, limit=limit)


def get_latest_news(db: Session, *, player_id: int):
    return repository.get_latest_news_for_player(db=db, player_id=player_id)
