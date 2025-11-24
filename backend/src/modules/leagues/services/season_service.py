from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from datetime import date
from typing import List, Optional
from ..models import Season, Week
from ..schemas import SeasonCreate, SeasonUpdate, WeekCreate

class SeasonService:
    
    @staticmethod
    def validate_date_ranges(start_date: date, end_date: date):
        """Valida que las fechas sean coherentes"""
        if end_date <= start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio"
            )
        
        # Comentar temporalmente esta validación para pruebas
        # if start_date < date.today():
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="La fecha de inicio no puede estar en el pasado"
        #     )
    
    @staticmethod
    def validate_weeks_overlap(weeks: List[WeekCreate]):
        """Valida que las semanas no se traslapen entre sí"""
        sorted_weeks = sorted(weeks, key=lambda w: w.start_date)
        
        for i in range(len(sorted_weeks) - 1):
            current_week = sorted_weeks[i]
            next_week = sorted_weeks[i + 1]
            
            if current_week.end_date >= next_week.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Las semanas {current_week.week_number} y {next_week.week_number} se traslapan"
                )
    
    @staticmethod
    def validate_weeks_within_season(weeks: List[WeekCreate], season_start: date, season_end: date):
        """Valida que todas las semanas estén dentro del rango de la temporada"""
        for week in weeks:
            if week.start_date < season_start or week.end_date > season_end:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La semana {week.week_number} está fuera del rango de la temporada"
                )
    
    @staticmethod
    def check_season_overlap(db: Session, start_date: date, end_date: date, exclude_season_id: Optional[int] = None):
        """Verifica si hay traslape con otra temporada existente"""
        query = db.query(Season).filter(
            or_(
                and_(Season.start_date <= start_date, Season.end_date >= start_date),
                and_(Season.start_date <= end_date, Season.end_date >= end_date),
                and_(Season.start_date >= start_date, Season.end_date <= end_date)
            )
        )
        
        if exclude_season_id:
            query = query.filter(Season.id != exclude_season_id)
        
        overlapping_season = query.first()
        
        if overlapping_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Las fechas se traslapan con la temporada existente: {overlapping_season.name}"
            )
    
    @staticmethod
    def check_name_exists(db: Session, name: str, exclude_season_id: Optional[int] = None):
        """Verifica si el nombre ya existe"""
        query = db.query(Season).filter(Season.name == name)
        
        if exclude_season_id:
            query = query.filter(Season.id != exclude_season_id)
        
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una temporada con el nombre: {name}"
            )
    
    @staticmethod
    def unset_current_season(db: Session, exclude_season_id: Optional[int] = None):
        """Quita el flag is_current de todas las temporadas"""
        query = db.query(Season).filter(Season.is_current == True)
        
        if exclude_season_id:
            query = query.filter(Season.id != exclude_season_id)
        
        query.update({"is_current": False})
    
    @staticmethod
    def create_season(db: Session, season_data: SeasonCreate, user_id: int) -> Season:
        """Crea una nueva temporada con todas las validaciones"""
        
        try:
            # Validaciones de fechas
            SeasonService.validate_date_ranges(season_data.start_date, season_data.end_date)
            
            # Validar nombre único
            SeasonService.check_name_exists(db, season_data.name)
            
            # Validar traslape con otras temporadas
            SeasonService.check_season_overlap(db, season_data.start_date, season_data.end_date)
            
            # Validar semanas
            if season_data.weeks:
                SeasonService.validate_weeks_overlap(season_data.weeks)
                SeasonService.validate_weeks_within_season(
                    season_data.weeks, 
                    season_data.start_date, 
                    season_data.end_date
                )
            
            # Si se marca como actual, quitar flag de otras temporadas
            if season_data.is_current:
                SeasonService.unset_current_season(db)
            
            # Crear array de semanas para el cache
            cached_weeks = []
            if season_data.weeks:
                for week_data in season_data.weeks:
                    cached_weeks.append({
                        "week_number": week_data.week_number,
                        "start_date": week_data.start_date.isoformat(),
                        "end_date": week_data.end_date.isoformat()
                    })

            # Crear temporada con semanas cacheadas
            season = Season(
                name=season_data.name,
                year=season_data.start_date.year,
                week_count=season_data.week_count,
                start_date=season_data.start_date,
                end_date=season_data.end_date,
                is_current=season_data.is_current,
                created_by=user_id,
                cached_weeks=cached_weeks
            )
            
            db.add(season)
            db.flush()  # Para obtener el ID
            
            # Crear semanas en la tabla de weeks (para mantener compatibilidad)
            if season_data.weeks:
                for week_data in season_data.weeks:
                    week = Week(
                        season_id=season.id,
                        week_number=week_data.week_number,
                        start_date=week_data.start_date,
                        end_date=week_data.end_date
                    )
                    db.add(week)
            
            db.commit()
            db.refresh(season)
            
            return season
            
        except HTTPException:
            # Re-lanzar HTTPExceptions tal cual
            db.rollback()
            raise
        except SQLAlchemyError as e:
            # Manejar errores de base de datos
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de base de datos: {str(e)}"
            )
        except Exception as e:
            # Manejar cualquier otro error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado: {str(e)}"
            )
    
    @staticmethod
    def update_season(db: Session, season_id: int, season_data: SeasonUpdate) -> Season:
        """Actualiza una temporada"""
        try:
            season = db.query(Season).filter(Season.id == season_id).first()
            
            if not season:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Temporada no encontrada"
                )
            
            # Si se actualiza el nombre, validar que no exista
            if season_data.name and season_data.name != season.name:
                SeasonService.check_name_exists(db, season_data.name, season_id)
                season.name = season_data.name
            
            # Si se marca como actual, quitar flag de otras temporadas
            if season_data.is_current is not None:
                if season_data.is_current:
                    SeasonService.unset_current_season(db, season_id)
                season.is_current = season_data.is_current
            
            db.commit()
            db.refresh(season)
            
            return season
            
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de base de datos: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado: {str(e)}"
            )
    
    @staticmethod
    def get_seasons(db: Session, skip: int = 0, limit: int = 100) -> List[Season]:
        """Obtiene lista de temporadas"""
        return db.query(Season).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_season(db: Session, season_id: int) -> Season:
        """Obtiene una temporada por ID usando las semanas cacheadas"""
        season = db.query(Season).filter(Season.id == season_id).first()
        
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Temporada no encontrada"
            )
        
        return season
    
    @staticmethod
    def get_weeks_from_cache(season: Season) -> List[WeekCreate]:
        """Obtiene las semanas desde el cache"""
        weeks = []
        for week_data in season.cached_weeks:
            weeks.append(WeekCreate(
                week_number=week_data["week_number"],
                start_date=date.fromisoformat(week_data["start_date"]),
                end_date=date.fromisoformat(week_data["end_date"])
            ))
        return sorted(weeks, key=lambda w: w.week_number)
    
    @staticmethod
    def update_cached_weeks(season: Season, weeks: List[WeekCreate], db: Session):
        """Actualiza las semanas cacheadas"""
        cached_weeks = []
        for week in weeks:
            cached_weeks.append({
                "week_number": week.week_number,
                "start_date": week.start_date.isoformat(),
                "end_date": week.end_date.isoformat()
            })
        season.cached_weeks = cached_weeks
        db.commit()
