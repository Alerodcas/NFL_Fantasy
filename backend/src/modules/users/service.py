from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ...config import auth as security
from . import models, schemas, repository


def register_user(db: Session, *, user: schemas.UserCreate) -> models.User:
    """
    Business logic for user registration:
    - Check if email already exists
    - Hash password
    - Create user record
    """
    existing = repository.get_user_by_email(db, email=user.email)
    if existing:
        raise ValueError("Email already registered")
    
    return repository.create_user(db, user=user)


def authenticate_user(db: Session, email: str, password: str, *, max_attempts: int = 5) -> models.User:
    """
    Authenticate user by email and password.
    Returns user on success, raises PermissionError on failure.
    Handles failed login attempts and account locking.
    """
    user = repository.get_user_by_email(db, email=email)
    
    if not user or not security.verify_password(password, user.hashed_password):
        if user:
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after max_attempts
            if user.failed_login_attempts >= max_attempts:
                user.account_status = "blocked"
                db.commit()
                raise PermissionError("Account locked due to too many failed attempts")
            
            db.commit()
        
        raise PermissionError("Invalid credentials")
    
    # Check if account is blocked
    if user.account_status == "blocked":
        raise PermissionError("Account is blocked")
    
    # Success: reset failed attempts and update last activity
    user.failed_login_attempts = 0
    user.last_activity = datetime.utcnow()
    db.commit()
    
    return user


def create_access_token_for_user(user: models.User, *, expires_hours: int = 24) -> str:
    """
    Create JWT access token for authenticated user.
    """
    return security.create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(hours=expires_hours)
    )


def update_user_profile(
    db: Session,
    user: models.User,
    *,
    name: Optional[str] = None,
    alias: Optional[str] = None,
    password: Optional[str] = None
) -> models.User:
    """
    Update user profile fields.
    """
    if name:
        user.name = name
    if alias:
        user.alias = alias
    if password:
        user.hashed_password = security.get_password_hash(password)
    
    db.commit()
    db.refresh(user)
    return user
