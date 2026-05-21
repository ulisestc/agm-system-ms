import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
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

# Configuración de JWT (Se sugiere pasar al .env más adelante)
SECRET_KEY = "clave_super_secreta_desarrollo_agm"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # El token dura 1 hora

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

# Endpoint de Login (Generación de Token JWT)
@app.post("/auth/login")
def login(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Buscar al usuario en la base de datos por su correo
    db_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    
    # 2. Si no existe o la contraseña no coincide, lanzamos error 401
    if not db_user or not verify_password(usuario.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    # 3. Si todo está bien, fabricamos el Token JWT con su ID y Rol
    access_token = create_access_token(
        data={"sub": str(db_user.id), "rol": db_user.rol}
    )
    
    # 4. Se lo entregamos al cliente
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para listar todos los usuarios (Útil para revisar los registros en la BD)
@app.get("/usuarios/", response_model=list[schemas.UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return usuarios