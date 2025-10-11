from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Annotated

from . import crud, models, schemas, security
from .database import engine, get_db

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
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        if user: # Si el usuario existe pero la contraseña es incorrecta
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.account_status = 'locked'
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.account_status != 'active':
        raise HTTPException(status_code=400, detail="Account is locked")
    
    # Resetear intentos fallidos en login exitoso
    user.failed_login_attempts = 0
    db.commit()
    
    access_token = security.create_access_token(data={"sub": user.email})
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