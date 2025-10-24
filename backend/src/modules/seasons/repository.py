from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, timedelta
from typing import List, Optional
from fastapi import HTTPException, status

from . import models, schemas


def _check_season_name_exists(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
    """Check if a season with the given name already exists."""
    query = db.query(models.Season).filter(models.Season.name == name)
    if exclude_id:
        query = query.filter(models.Season.id != exclude_id)
    return query.first() is not None


def _check_date_overlap(db: Session, start_date: date, end_date: date, exclude_id: Optional[int] = None) -> Optional[models.Season]:
    """Check if dates overlap with any existing season."""
    query = db.query(models.Season).filter(
        or_(
            # New season starts during existing season
            and_(models.Season.start_date <= start_date, models.Season.end_date >= start_date),
            # New season ends during existing season
            and_(models.Season.start_date <= end_date, models.Season.end_date >= end_date),
            # New season completely contains existing season
            and_(models.Season.start_date >= start_date, models.Season.end_date <= end_date)
        )
    )
    if exclude_id:
        query = query.filter(models.Season.id != exclude_id)
    return query.first()


def _generate_weeks(season_start: date, season_end: date, num_weeks: int) -> List[dict]:
    """Generate week dates evenly distributed across the season."""
    total_days = (season_end - season_start).days + 1
    days_per_week = total_days / num_weeks
    
    weeks = []
    for i in range(num_weeks):
        week_start = season_start + timedelta(days=int(i * days_per_week))
        
        if i == num_weeks - 1:
            # Last week ends on season end date
            week_end = season_end
        else:
            week_end = season_start + timedelta(days=int((i + 1) * days_per_week) - 1)
        
        # Ensure week end doesn't exceed season end
        if week_end > season_end:
            week_end = season_end
            
        weeks.append({
            "week_number": i + 1,
            "start_date": week_start,
            "end_date": week_end
        })
    
    return weeks


def _validate_weeks_no_overlap(weeks: List[dict]) -> None:
    """Validate that weeks don't overlap with each other."""
    for i in range(len(weeks) - 1):
        if weeks[i]["end_date"] >= weeks[i + 1]["start_date"]:
            raise ValueError(f"Week {weeks[i]['week_number']} overlaps with week {weeks[i + 1]['week_number']}")


def get_season(db: Session, season_id: int) -> Optional[models.Season]:
    """Get a season by ID."""
    return db.query(models.Season).filter(models.Season.id == season_id).first()


def get_seasons(db: Session, skip: int = 0, limit: int = 100) -> List[models.Season]:
    """Get all seasons with pagination."""
    return db.query(models.Season).order_by(models.Season.created_at.desc()).offset(skip).limit(limit).all()


def get_current_season(db: Session) -> Optional[models.Season]:
    """Get the current active season."""
    return db.query(models.Season).filter(models.Season.is_current == True).first()


def create_season(db: Session, season: schemas.SeasonCreate) -> models.Season:
    """Create a new season with auto-generated weeks."""
    # Validate name uniqueness
    if _check_season_name_exists(db, season.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A season with the name '{season.name}' already exists"
        )
    
    # Validate date overlap
    overlapping_season = _check_date_overlap(db, season.start_date, season.end_date)
    if overlapping_season:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Season dates overlap with existing season '{overlapping_season.name}' ({overlapping_season.start_date} to {overlapping_season.end_date})"
        )
    
    # If marking as current, unmark any existing current season
    if season.is_current:
        existing_current = get_current_season(db)
        if existing_current:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Season '{existing_current.name}' is already marked as current. Only one season can be current at a time."
            )
    
    # Generate weeks
    weeks_data = _generate_weeks(season.start_date, season.end_date, season.num_weeks)
    
    # Validate weeks don't overlap
    _validate_weeks_no_overlap(weeks_data)
    
    # Create season
    db_season = models.Season(
        name=season.name,
        start_date=season.start_date,
        end_date=season.end_date,
        is_current=season.is_current
    )
    db.add(db_season)
    db.flush()  # Get the season ID
    
    # Create weeks
    for week_data in weeks_data:
        db_week = models.Week(
            season_id=db_season.id,
            **week_data
        )
        db.add(db_week)
    
    db.commit()
    db.refresh(db_season)
    return db_season


def update_season(db: Session, season_id: int, season_update: schemas.SeasonUpdate) -> models.Season:
    """Update an existing season."""
    db_season = get_season(db, season_id)
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found"
        )
    
    # Validate name uniqueness if name is being updated
    if season_update.name is not None and season_update.name != db_season.name:
        if _check_season_name_exists(db, season_update.name, exclude_id=season_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A season with the name '{season_update.name}' already exists"
            )
        db_season.name = season_update.name
    
    # Validate date overlap if dates are being updated
    start_date = season_update.start_date if season_update.start_date is not None else db_season.start_date
    end_date = season_update.end_date if season_update.end_date is not None else db_season.end_date
    
    if season_update.start_date is not None or season_update.end_date is not None:
        if end_date <= start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        overlapping_season = _check_date_overlap(db, start_date, end_date, exclude_id=season_id)
        if overlapping_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Season dates overlap with existing season '{overlapping_season.name}' ({overlapping_season.start_date} to {overlapping_season.end_date})"
            )
        
        if season_update.start_date is not None:
            db_season.start_date = season_update.start_date
        if season_update.end_date is not None:
            db_season.end_date = season_update.end_date
    
    # Handle is_current flag
    if season_update.is_current is not None:
        if season_update.is_current and not db_season.is_current:
            # User wants to mark this as current
            existing_current = get_current_season(db)
            if existing_current and existing_current.id != season_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Season '{existing_current.name}' is already marked as current. Only one season can be current at a time."
                )
        db_season.is_current = season_update.is_current
    
    db.commit()
    db.refresh(db_season)
    return db_season


def delete_season(db: Session, season_id: int) -> bool:
    """Delete a season and its weeks."""
    db_season = get_season(db, season_id)
    if not db_season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with id {season_id} not found"
        )
    
    db.delete(db_season)
    db.commit()
    return True
