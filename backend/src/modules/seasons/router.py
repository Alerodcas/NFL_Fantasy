from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ...config.database import get_db
from ...core import audit
from ..users.router import get_current_user
from ..users import models as user_models
from . import repository as crud, schemas

router = APIRouter(prefix="/seasons", tags=["seasons"])


def require_admin(current_user: Annotated[user_models.User, Depends(get_current_user)]):
    """Dependency to ensure the user is an administrator."""
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user


@router.post("/", response_model=schemas.SeasonCreated, status_code=201)
async def create_season(
    request: Request,
    season: schemas.SeasonCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(require_admin),
):
    """Create a new season with auto-generated weeks. Admin only."""
    try:
        created_season = crud.create_season(db=db, season=season)
        audit.log_event(
            action="create_season",
            user_id=str(current_user.id),
            status="SUCCESS",
            details=f'Season "{created_season.name}" created with {len(created_season.weeks)} weeks',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        return created_season
    except HTTPException as he:
        audit.log_event(
            action="create_season",
            user_id=str(current_user.id),
            status="FAILED",
            details=f"Failed to create season: {he.detail}",
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        raise
    except Exception as e:
        audit.log_event(
            action="create_season",
            user_id=str(current_user.id),
            status="ERROR",
            details=f"Error creating season: {str(e)}",
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create season",
        )


@router.get("/", response_model=List[schemas.SeasonCreated])
async def list_seasons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    """List all seasons. Authenticated users only."""
    return crud.get_seasons(db, skip=skip, limit=limit)


@router.get("/current", response_model=schemas.SeasonCreated)
async def get_current_season(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    """Get the current active season. Authenticated users only."""
    season = crud.get_current_season(db)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current season found",
        )
    return season


@router.get("/{season_id}", response_model=schemas.SeasonCreated)
async def get_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    """Get a specific season by ID. Authenticated users only."""
    season = crud.get_season(db, season_id=season_id)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found",
        )
    return season


@router.put("/{season_id}", response_model=schemas.SeasonCreated)
async def update_season(
    request: Request,
    season_id: int,
    season_update: schemas.SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(require_admin),
):
    """Update a season. Admin only."""
    try:
        updated_season = crud.update_season(db=db, season_id=season_id, season_update=season_update)
        audit.log_event(
            action="update_season",
            user_id=str(current_user.id),
            status="SUCCESS",
            details=f'Season "{updated_season.name}" (ID: {season_id}) updated',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        return updated_season
    except HTTPException as he:
        audit.log_event(
            action="update_season",
            user_id=str(current_user.id),
            status="FAILED",
            details=f"Failed to update season ID {season_id}: {he.detail}",
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        raise


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    request: Request,
    season_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(require_admin),
):
    """Delete a season and its weeks. Admin only."""
    try:
        crud.delete_season(db=db, season_id=season_id)
        audit.log_event(
            action="delete_season",
            user_id=str(current_user.id),
            status="SUCCESS",
            details=f"Season ID {season_id} deleted",
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        return None
    except HTTPException as he:
        audit.log_event(
            action="delete_season",
            user_id=str(current_user.id),
            status="FAILED",
            details=f"Failed to delete season ID {season_id}: {he.detail}",
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            masked_data=False,
        )
        raise
