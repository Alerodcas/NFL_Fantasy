from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, ForeignKey
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

