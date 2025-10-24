from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ...config.database import Base

class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    num_weeks = Column(Integer, nullable=False)
    is_current = Column(Boolean, default=False)

    # Use string name for relationship
    weeks = relationship("Week", back_populates="season")

class Week(Base):
    __tablename__ = "weeks"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    season = relationship("Season", back_populates="weeks")
    
    __table_args__ = (
        # Ensure week_number is unique per season
        # This would be a unique constraint in production
    )
