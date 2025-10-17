from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Annotated

from .modules.users import repository as crud, models, schemas
from .core import audit
from .config.database import engine, get_db
from .modules.teams.schemas import TeamCreate, Team
from .config import auth as security
from sqlalchemy import text

# Crea las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS ANTES de las rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Error de validación: {exc}")
    print(f"Detalles del error: {exc.errors()}")
    
    # Leer el cuerpo de la petición para ver qué datos llegaron
    try:
        body = await request.body()
        print(f"Raw request body: {body}")
        import json
        data = json.loads(body)
        print(f"Parsed data: {data}")
        if 'password' in data:
            password = data['password']
            print(f"Password length (chars): {len(password)}")
            print(f"Password length (bytes): {len(password.encode('utf-8'))}")
            print(f"Password repr: {repr(password)}")
    except Exception as e:
        print(f"Error al leer el cuerpo: {e}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Error de validación", "errors": exc.errors()}
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función de dependencia para obtener el usuario actual a partir del token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    if user.account_status != 'active':
         raise HTTPException(status_code=400, detail="Account is locked or inactive")
         
    return user

@app.post("/register/", response_model=schemas.User)
async def register_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Leer el cuerpo de la petición para debugging
    body = await request.body()
    print(f"Raw request body: {body}")
    
    print(f"Registro recibido: name={user.name}, email={user.email}, alias={user.alias}")
    print(f"Password length (chars): {len(user.password)}")
    print(f"Password length (bytes): {len(user.password.encode('utf-8'))}")
    print(f"Password repr: {repr(user.password)}")
    print(f"First 100 chars of password: {user.password[:100]}")
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        audit.log_event(
            action='register_attempt',
            user_id=user.email,  # Usamos el email porque el ID de usuario aún no existe
            status='FAILED',
            details='Attempt to register with an already existing email',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        created_user = crud.create_user(db=db, user=user)
        audit.log_event(
            action='register',
            user_id=str(created_user.id),
            status='SUCCESS',
            details='User registered successfully',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=False,
        )
        return created_user
    except Exception as e:
        # Log de error si la creación del usuario falla por alguna razón
        audit.log_event(
            action='register_attempt',
            user_id=user.email,
            status='FAILED',
            details=f'User creation failed: {e}',
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            masked_data=True,
        )
        # Re-lanzar la excepción para que FastAPI la maneje
        raise HTTPException(status_code=500, detail="Could not create user.")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        source_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')

        if user:  # Si el usuario existe pero la contraseña es incorrecta
            user.failed_login_attempts += 1
            # Si alcanza 3 intentos fallidos, bloquear la cuenta y devolver mensaje específico
            if user.failed_login_attempts >= 3:
                user.account_status = 'locked'
                db.commit()
                # Registrar evento de auditoría: cuenta bloqueada
                audit.log_event(
                    action='login_attempt',
                    user_id=str(user.id),
                    status='FAILED_LOCKED',
                    details=f'User locked after failed attempts',
                    source_ip=source_ip,
                    user_agent=user_agent,
                    masked_data=True,
                )
                raise HTTPException(
                    status_code=400,
                    detail="Cuenta bloqueada",
                )
            db.commit()

            # Registrar intento fallido normal
            audit.log_event(
                action='login_attempt',
                user_id=str(user.id),
                status='FAILED',
                details=f'Incorrect password, attempt {user.failed_login_attempts}',
                source_ip=source_ip,
                user_agent=user_agent,
                masked_data=True,
            )

        # Mensaje genérico para evitar enumeración de usuarios
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.account_status != 'active':
        source_ip = None
        user_agent = None
        # Intentamos leer datos del request si están disponibles (no en todos los paths)
        try:
            # `request` estará disponible en este scope because it's a param earlier
            source_ip = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent')
        except Exception:
            pass

        audit.log_event(
            action='login_attempt',
            user_id=str(user.id),
            status='FAILED_LOCKED',
            details='Login attempt on locked account',
            source_ip=source_ip,
            user_agent=user_agent,
            masked_data=True,
        )

        # Devolver mensaje en español para que el frontend pueda mostrar "Cuenta bloqueada"
        raise HTTPException(status_code=400, detail="Cuenta bloqueada")
    
    # Resetear intentos fallidos en login exitoso
    user.failed_login_attempts = 0
    db.commit()
    
    access_token = security.create_access_token(data={"sub": user.email})
    # Registrar evento de auditoría: login exitoso
    try:
        source_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
    except Exception:
        source_ip = None
        user_agent = None

    audit.log_event(
        action='login',
        user_id=str(user.id),
        status='SUCCESS',
        details='User logged in successfully',
        source_ip=source_ip,
        user_agent=user_agent,
        masked_data=False,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user

@app.put("/users/me/", response_model=schemas.User)
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

# --- Helpers internos para Teams ---
def _ensure_manager_or_above(current_user):
    # Usa el mismo campo 'role'
    role = getattr(current_user, "role", None)
    if role not in ("manager", "admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role"
        )

def _assert_league_exists(db: Session, league_id: int):
    row = db.execute(
        text("SELECT 1 FROM leagues WHERE id = :lid"),
        {"lid": league_id}
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")


# --- Feature 3.1: Crear Equipo ---
@app.post("/teams", response_model=Team, status_code=status.HTTP_201_CREATED, tags=["teams"])
def create_team(
    payload: TeamCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # 1) Permisos: solo manager+ crea equipo
    _ensure_manager_or_above(current_user)

    # 2) Integridad: la liga debe existir
    league_exists = db.execute(
        text("SELECT 1 FROM leagues WHERE id = :lid"),
        {"lid": payload.league_id}
    ).first()

    if not league_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with ID {payload.league_id} not found"
        )

    # 3) Unicidad: nombre único dentro de la liga
    exists = db.execute(
        text("SELECT 1 FROM teams WHERE league_id = :lid AND name = :nm"),
        {"lid": payload.league_id, "nm": payload.name}
    ).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name already used in this league"
        )

    # 4) Insertar y devolver el equipo creado
    result = db.execute(
        text("""
            INSERT INTO teams (league_id, owner_user_id, name, description, logo_url)
            VALUES (:lid, :owner, :name, :desc, :logo)
            RETURNING id, league_id, owner_user_id, name, description, logo_url, created_at
        """),
        {
            "lid": payload.league_id,
            "owner": current_user.id,
            "name": payload.name,
            "desc": payload.description,
            "logo": str(payload.logo_url) if payload.logo_url else None,
        }
    )

    db.commit()
    row = result.first()
    return {
        "id": row.id,
        "league_id": row.league_id,
        "owner_user_id": row.owner_user_id,
        "name": row.name,
        "description": row.description,
        "logo_url": row.logo_url,
        "created_at": row.created_at,
    }
