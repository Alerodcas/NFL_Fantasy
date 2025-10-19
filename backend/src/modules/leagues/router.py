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
        league, team = crud.create_league_with_commissioner_team(
            db=db, creator_user_id=current_user.id, payload=payload
        )
    except ValueError as ve:
        if "already exists" in str(ve):
            raise HTTPException(status_code=409, detail="A league with that name already exists.")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=409, detail=str(re))
    except Exception:
        raise HTTPException(status_code=500, detail="Could not create league.")

    slots_remaining = int(league.max_teams) - 1
    resp = schemas.LeagueCreated(
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


    try:
        if hasattr(audit, "log_event"):
            audit.log_event(
                action="create_league",
                user_id=str(current_user.id),
                status="SUCCESS",
                details=f"league_id={league.id}",
                source_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
    except Exception:
        pass

    return resp
