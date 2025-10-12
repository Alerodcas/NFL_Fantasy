from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a tu base de datos PostgreSQL
# Formato: "postgresql://user:password@host/dbname"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:160103@localhost/nfl_fantasy"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:07122002@localhost/NFL_Fantasy"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()