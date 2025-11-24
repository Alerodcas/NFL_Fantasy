from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey, Index, text, JSON
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


class PlayerNews(Base):
    __tablename__ = "player_news"

    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    summary = Column(String(30), nullable=False)
    text = Column(String(300), nullable=False)
    is_injury = Column(Boolean, nullable=False, default=False)
    injury_type = Column(String(10), nullable=True)
    changes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_player_news_player_id", "player_id")
Index("ix_player_news_created_at", "created_at")
