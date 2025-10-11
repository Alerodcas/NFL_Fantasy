from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuración de seguridad
SECRET_KEY = "un-secreto-muy-seguro-debes-cambiar-esto" # CAMBIA ESTO EN PRODUCCIÓN
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12 horas

# Contexto para hashear contraseñas con configuración simple
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt