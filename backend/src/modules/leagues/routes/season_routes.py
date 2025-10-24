from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ....config.database import get_db
from ...users.router import get_current_user
from ...users.models import User
from ..schemas import SeasonCreate, SeasonUpdate, SeasonResponse
from ..services.season_service import SeasonService

router = APIRouter(prefix="/seasons", tags=["seasons"])

def verify_admin(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario sea administrador"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return current_user

@router.post("/", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
def create_season(
    season_data: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Crea una nueva temporada (solo administradores).
    
    Validaciones:
    - Nombre único (1-100 caracteres)
    - Fecha de fin posterior a fecha de inicio
    - Fechas no en el pasado
    - Sin traslape con otras temporadas
    - Semanas sin traslape entre sí
    - Semanas dentro del rango de la temporada
    - Solo una temporada puede ser actual
    """
    season = SeasonService.create_season(db, season_data, current_user.id)
    return season

@router.get("/", response_model=List[SeasonResponse])
def get_seasons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene lista de temporadas"""
    seasons = SeasonService.get_seasons(db, skip, limit)
    return seasons

@router.get("/{season_id}", response_model=SeasonResponse)
def get_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una temporada por ID"""
    season = SeasonService.get_season(db, season_id)
    return season

@router.patch("/{season_id}", response_model=SeasonResponse)
def update_season(
    season_id: int,
    season_data: SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Actualiza una temporada (solo administradores).
    
    Permite actualizar:
    - Nombre
    - Estado is_current
    """
    season = SeasonService.update_season(db, season_id, season_data)
    return season
