from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from ...config.database import Base

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    week_count = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, nullable=False, server_default=text("FALSE"))
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    weeks = relationship("Week", back_populates="season", cascade="all, delete-orphan")
    leagues = relationship("League", back_populates="season")

class Week(Base):
    __tablename__ = "weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    season = relationship("Season", back_populates="weeks")

class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(1000))
    max_teams = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, server_default=text("'pre_draft'"))
    allow_decimal_scoring = Column(Boolean, nullable=False, server_default=text("TRUE"))
    playoff_format = Column(Integer, nullable=False)  # 4 or 6
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="RESTRICT"))
    trade_deadline = Column(DateTime(timezone=True))
    max_trades_per_team = Column(Integer)
    max_free_agents_per_team = Column(Integer)
    roster_schema = Column(JSONB, nullable=False)
    scoring_schema = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    season = relationship("Season", back_populates="leagues")
