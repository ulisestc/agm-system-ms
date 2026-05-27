import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Conexión a la base de datos que creamos en el init.sql
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:root@postgres-db:5432/agm_calificaciones_db")

# SQLAlchemy 2.0 no soporta 'postgres://', debe ser 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()