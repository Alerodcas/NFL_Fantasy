from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey, Index, text
from ...config.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    position = Column(String(64), nullable=False)
    image_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    team_id = Column(BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

# Unique within a team (case-insensitive name)
Index(
    "ux_players_team_name",
    "team_id",
    text("LOWER(name)"),
    unique=True,
)

Index("ix_players_team_id", "team_id")
