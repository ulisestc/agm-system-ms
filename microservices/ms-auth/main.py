from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import engine, Base, get_db
import models, schemas

# Le decimos a la base de datos que cree las tablas si no existen
Base.metadata.create_all(bind=engine)

# Configuración para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="MS-1 Auth & Users",
    description="Microservicio de Autenticación para el sistema AGM",
    version="1.0.0"
)


# RUTAS (ENDPOINTS)

@app.get("/")
def read_root():
    return {"mensaje": "¡El microservicio de Auth está corriendo!"}

# Endpoint para crear (registrar) un nuevo usuario
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    
    # 1. Verificar si el correo ya está registrado en la BD
    db_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado")
    
    # 2. Encriptar la contraseña
    hashed_password = get_password_hash(usuario.password)
    
    # 3. Preparar el usuario para guardarlo (usando el modelo de base de datos)
    nuevo_usuario = models.Usuario(
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol
    )
    
    # 4. Guardarlo en PostgreSQL
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # 5. Devolver el usuario recién creado
    return nuevo_usuario