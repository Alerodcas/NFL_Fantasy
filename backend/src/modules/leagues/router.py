from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...core import audit
from ..users.router import get_current_user
from . import repository as crud, schemas
from ...core.media import ensure_subdir, make_thumb_from_path, public_url

router = APIRouter(prefix="/leagues", tags=["leagues"])

@router.post("", response_model=schemas.LeagueCreated, status_code=201)
def create_league(
    payload: schemas.LeagueCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    print(f"[DEBUG] Payload recibido en backend: {payload}")
    try:
        if hasattr(audit, "log_event"):
            audit.log_event(
                action="create_league_attempt",
                user_id=str(current_user.id),
                status="PENDING",
                details=f"league={payload.name}",
                source_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
    except Exception:
        pass

    try:
        print("[DEBUG] Llamando a create_league_with_commissioner_team")
        league, team = crud.create_league_with_commissioner_team(
            db=db, creator_user_id=current_user.id, payload=payload
        )
        print("[DEBUG] create_league_with_commissioner_team completado exitosamente")
    except LookupError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        msg = str(ve)
        if "already exists" in msg or "already assigned" in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except RuntimeError as re:
        raise HTTPException(status_code=409, detail=str(re))
    except Exception as e:
        print(f"[DEBUG] Error en create_league_with_commissioner_team: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not create league.")

    slots_remaining = int(league.max_teams) - 1
    return schemas.LeagueCreated(
        id=league.id,
        uuid=str(league.uuid) if getattr(league, "uuid", None) else None,
        name=league.name,
        status=league.status,
        max_teams=league.max_teams,
        playoff_format=league.playoff_format,
        allow_decimal_scoring=bool(league.allow_decimal_scoring),
        season_id=league.season_id,
        slots_remaining=slots_remaining,
        commissioner_team_id=team.id,
    )


@router.get("/search", response_model=list[schemas.LeagueSearchResult])
def search_leagues(
    name: str | None = None,
    season_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Busca ligas solo cuando se proporciona un criterio concreto.
    Reglas de seguridad para evitar listar ligas sin búsqueda:
    - Se requiere al menos un criterio (name, season_id o status)
    - Si se usa name, debe tener al menos 3 caracteres (case-insensitive)
    """
    # Evitar la enumeración de ligas sin un término de búsqueda explícito
    if not any([name, season_id, status]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un criterio de búsqueda (name, season_id o status)."
        )

    if name is not None:
        cleaned = name.strip()
        if len(cleaned) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El parámetro 'name' debe tener al menos 3 caracteres."
            )
        name = cleaned

    filters = schemas.LeagueSearchFilters(
        name=name,
        season_id=season_id,
        status=status
    )

    results = crud.search_leagues(db=db, filters=filters)
    return results


@router.post("/{league_id}/join", response_model=schemas.JoinLeagueResponse, status_code=201)
def join_league(
    league_id: int,
    payload: schemas.JoinLeagueRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Une al usuario actual a una liga existente.
    Requiere:
    - password: contraseña de la liga
    - user_alias: alias único del usuario en esta liga
    - fantasy_team: datos del equipo de fantasía (name, image_url opcional)
    
    Validaciones:
    - Liga existe y está activa
    - Contraseña correcta
    - Hay cupos disponibles
    - Usuario no está ya en la liga
    - Alias único en la liga
    - Nombre de equipo único en la liga
    """
    
    # Registrar intento de unión
    try:
        if hasattr(audit, "log_event"):
            audit.log_event(
                action="join_league_attempt",
                user_id=str(current_user.id),
                status="PENDING",
                details=f"league_id={league_id}, fantasy_team={getattr(payload, 'fantasy_team', None)}",
                source_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
    except Exception:
        pass
    
    try:
        member = crud.join_league(
            db=db,
            league_id=league_id,
            user_id=current_user.id,
            payload=payload
        )
        
        # Registrar éxito en auditoría
        try:
            if hasattr(audit, "log_event"):
                audit.log_event(
                    action="join_league_success",
                    user_id=str(current_user.id),
                    status="SUCCESS",
                    details=f"league_id={league_id}, alias={payload.user_alias}",
                    source_ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
        except Exception:
            pass
        
        return schemas.JoinLeagueResponse(
            message="Te has unido exitosamente a la liga",
            league_id=member.league_id,
            team_id=member.fantasy_team_id,
            user_alias=member.user_alias,
            joined_at=member.joined_at
        )
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        # Error genérico para contraseña incorrecta por seguridad
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        # Errores de validación (cupos, duplicados, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[DEBUG] Error en join_league: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="No se pudo unir a la liga.")


@router.post("/fantasy-team/upload", status_code=201)
def upload_fantasy_team_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Subida de imagen para equipos de fantasía. Devuelve URLs públicas de la imagen y su thumbnail.
    Esto permite a los formularios enviar un archivo y luego usar la URL resultante en la creación/unión de liga.
    """
    # Guardar archivo bajo media/fantasy_teams y generar thumbnail
    ft_dir = ensure_subdir("fantasy_teams")
    filename = image.filename or "upload.png"
    import os, uuid
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"
    uid = uuid.uuid4().hex
    img_path = ft_dir / f"{uid}{ext}"
    try:
        with open(img_path, "wb") as f:
            f.write(image.file.read())
        image.file.seek(0)
        thumb_path = make_thumb_from_path(img_path)
    finally:
        try:
            image.file.close()
        except Exception:
            pass

    return {
        "image_url": public_url(img_path),
        "thumbnail_url": public_url(thumb_path),
    }

