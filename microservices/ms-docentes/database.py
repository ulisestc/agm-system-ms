import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Leemos la URL desde variables de entorno (idéntico patrón a ms-auth)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:root@localhost:5432/agm_docentes_db"
)

# SQLAlchemy 2.0 no soporta 'postgres://', debe ser 'postgresql://'
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Motor de conexión a PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base declarativa (SQLAlchemy 2.x estilo moderno)
class Base(DeclarativeBase):
    pass


# Dependencia inyectable en FastAPI (patrón ms-auth)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
