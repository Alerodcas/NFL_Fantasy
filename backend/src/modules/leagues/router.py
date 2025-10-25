from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...core import audit
from ..users.router import get_current_user
from . import repository as crud, schemas

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
    name: str = None,
    season_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Busca ligas por nombre, temporada y/o estado.
    - name: búsqueda parcial por nombre (case-insensitive)
    - season_id: filtrar por ID de temporada
    - status: filtrar por estado (pre_draft, draft, in_season, completed)
    """
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
    - team_id: ID del equipo a usar (debe ser del usuario y no estar en otra liga)
    
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
                details=f"league_id={league_id}, team_id={payload.team_id}",
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
                    details=f"league_id={league_id}, team_id={payload.team_id}, alias={payload.user_alias}",
                    source_ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
        except Exception:
            pass
        
        return schemas.JoinLeagueResponse(
            message="Te has unido exitosamente a la liga",
            league_id=member.league_id,
            team_id=member.team_id,
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

