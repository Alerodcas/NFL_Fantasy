from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey, Index, text
from ...config.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(128), nullable=False)         # DB has CITEXT UNIQUE(name)
    city = Column(String(128), nullable=False)
    image_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id", ondelete="CASCADE"), nullable=True)

# === Partial unique indexes (mirror the SQL in setup/fix) ===
# Unique among league-less teams
Index(
    "ux_teams_name_when_no_league",
    text("LOWER(name)"),
    unique=True,
    postgresql_where=text("league_id IS NULL"),
)

# Unique among teams with a league (league_id, name)
Index(
    "ux_teams_league_name",
    "league_id",
    text("LOWER(name)"),
    unique=True,
    postgresql_where=text("league_id IS NOT NULL"),
)

# Helper
<<<<<<< HEAD
Index("ix_teams_league_id", "league_id")
=======
Index("ix_teams_league_id", "league_id")
>>>>>>> main
