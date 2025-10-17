from sqlalchemy import Column, Integer, String, DateTime, func
from ...config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    alias = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    profile_image_url = Column(String(255), default='default_profile.png')
    language = Column(String(10), default='en')
    role = Column(String(20), default='manager')
    account_status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    failed_login_attempts = Column(Integer, default=0)
