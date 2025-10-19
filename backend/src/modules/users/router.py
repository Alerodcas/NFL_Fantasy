from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt

from ...config.database import get_db
from ...config import auth as security
from ...core import audit
from . import repository as crud, models, schemas

router = APIRouter()

oauth2_scheme = getattr(security, "oauth2_scheme", OAuth2PasswordBearer(tokenUrl="/token"))


# Dependency to get current user from token (copied from your main.py)
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # decode via helper if present, else fallback
    try:
        if hasattr(security, "jwt_decode"):
            payload = security.jwt_decode(token)
        else:
            payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    if user.account_status != 'active':
        raise HTTPException(status_code=400, detail="Account is locked or inactive")
    return user

@router.post("/register/", response_model=schemas.User)
async def register_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        audit.log_event(
            action='register_attempt', user_id=user.email, status='FAILED',
            details='Attempt to register with an already existing email',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        created_user = crud.create_user(db=db, user=user)
        audit.log_event(
            action='register', user_id=str(created_user.id), status='SUCCESS',
            details='User registered successfully',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=False,
        )
        return created_user
    except Exception as e:
        audit.log_event(
            action='register_attempt', user_id=user.email, status='FAILED',
            details=f'User creation failed: {e}',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        raise HTTPException(status_code=500, detail="Could not create user.")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        source_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 3:
                user.account_status = 'locked'
                db.commit()
                audit.log_event(
                    action='login_attempt', user_id=str(user.id), status='FAILED_LOCKED',
                    details='User locked after failed attempts',
                    source_ip=source_ip, user_agent=user_agent, masked_data=True,
                )
                raise HTTPException(status_code=400, detail="Cuenta bloqueada")
            db.commit()
            audit.log_event(
                action='login_attempt', user_id=str(user.id), status='FAILED',
                details=f'Incorrect password, attempt {user.failed_login_attempts}',
                source_ip=source_ip, user_agent=user_agent, masked_data=True,
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != 'active':
        audit.log_event(
            action='login_attempt', user_id=str(user.id), status='FAILED_LOCKED',
            details='Login attempt on locked account',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        raise HTTPException(status_code=400, detail="Cuenta bloqueada")

    user.failed_login_attempts = 0
    db.commit()
    access_token = security.create_access_token(data={"sub": user.email})
    audit.log_event(
        action='login', user_id=str(user.id), status='SUCCESS', details='User logged in successfully',
        source_ip=request.client.host if request.client else None,
        user_agent=request.headers.get('user-agent'),
        masked_data=False,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user

@router.put("/users/me/", response_model=schemas.User)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if user_update.name:
        current_user.name = user_update.name
    if user_update.alias:
        current_user.alias = user_update.alias
    if user_update.password:
        current_user.hashed_password = security.get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user
