from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from datetime import timedelta, datetime

from ...config.database import get_db
from ...config import auth as security
from ...core import audit
from . import repository as crud, models, schemas, service

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
    try:
        created_user = service.register_user(db=db, user=user)
        audit.log_event(
            action='register', user_id=str(created_user.id), status='SUCCESS',
            details='User registered successfully',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=False,
        )
        return created_user
    except ValueError as ve:
        audit.log_event(
            action='register_attempt', user_id=user.email, status='FAILED',
            details=str(ve),
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        raise HTTPException(status_code=400, detail=str(ve))
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
    source_ip = request.client.host if request.client else None
    user_agent = request.headers.get('user-agent')
    
    try:
        user = service.authenticate_user(db, form_data.username, form_data.password)
        
        access_token = service.create_access_token_for_user(user)
        audit.log_event(
            action='login', user_id=str(user.id), status='SUCCESS', details='User logged in successfully',
            source_ip=source_ip, user_agent=user_agent, masked_data=False,
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except PermissionError as pe:
        # Get user for audit logging
        user = crud.get_user_by_email(db, email=form_data.username)
        error_msg = str(pe)
        
        if "locked" in error_msg.lower() or "blocked" in error_msg.lower():
            if user:
                audit.log_event(
                    action='login_attempt', user_id=str(user.id), status='FAILED_LOCKED',
                    details=f'Account locked - {error_msg}',
                    source_ip=source_ip, user_agent=user_agent, masked_data=True,
                )
            raise HTTPException(status_code=400, detail="Cuenta bloqueada")
        else:
            if user:
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

@router.post("/login", response_model=schemas.LoginResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        user = service.authenticate_user(db, login_data.email, login_data.password, max_attempts=5)
        
        # Login exitoso: actualizar actividad
        user.last_activity = datetime.utcnow()
        db.commit()
        
        # Token de larga duración (24h), inactividad controlada por last_activity
        access_token = security.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(hours=24)
        )
        
        return schemas.LoginResponse(
            access_token=access_token,
            user_id=user.id
        )
    except PermissionError as pe:
        error_msg = str(pe)
        # Check if account is blocked vs credentials incorrect
        if "locked" in error_msg.lower() or "blocked" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta Bloqueada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales Incorrectas"
            )

@router.post("/logout", response_model=schemas.MessageResponse)
def logout(current_user: models.User = Depends(get_current_user)):
    # En arquitectura JWT stateless, el logout es del lado del cliente
    # El cliente debe eliminar el token
    return schemas.MessageResponse(message="Sesión cerrada exitosamente")

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user

@router.put("/users/me/", response_model=schemas.User)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    updated_user = service.update_user_profile(
        db=db,
        user=current_user,
        name=user_update.name,
        alias=user_update.alias,
        password=user_update.password
    )
    return updated_user
