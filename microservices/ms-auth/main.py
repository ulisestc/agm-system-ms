import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import engine, Base, get_db
import models, schemas

# Inicializa las tablas en la base de datos de PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

# Configuración del contexto para encriptación de contraseñas (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración para la generación y firma de JSON Web Tokens (JWT)
SECRET_KEY = "clave_super_secreta_desarrollo_agm"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # El token tendrá validez de 1 hora




# FUNCIONES AUXILIARES (SEGURIDAD Y HASHING)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




# GUARDIÁN DE SESIÓN (DEPENDENCIAS DE FASTAPI)


# Indica a FastAPI que el token de portador (Bearer Token) se obtiene en la ruta /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Desencriptación y lectura del payload del token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credenciales_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El token ha caducado")
    except jwt.InvalidTokenError:
        raise credenciales_exception
    
    # Búsqueda del usuario correspondiente en la base de datos
    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise credenciales_exception
        
    return usuario


# INICIALIZACIÓN DE LA APLICACIÓN
# ---------------------------------------------------------

app = FastAPI(
    title="MS-1 Auth & Users",
    description="Microservicio de Autenticación para el sistema AGM",
    version="1.0.0"
)


# ENDPOINTS (RUTAS REST)
# ---------------------------------------------------------

@app.get("/")
def read_root():
    return {"mensaje": "¡El microservicio de Auth está corriendo!"}

# Endpoint para registrar nuevos usuarios en el sistema
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Validación de duplicados por correo electrónico
    db_user = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado")
    
    # 2. Cifrado irreversible de la contraseña recibida
    hashed_password = get_password_hash(usuario.password)
    
    # 3. Mapeo al modelo ORM y persistencia en PostgreSQL
    nuevo_usuario = models.Usuario(
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# Endpoint de Login mapeado para interactuar con el flujo nativo de formularios de Swagger
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # El campo 'username' del formulario se evalúa contra la columna de email
    db_user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    # Emisión del token JWT con el identificador del usuario y su rol asignado
    access_token = create_access_token(
        data={"sub": str(db_user.id), "rol": db_user.rol}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint administrativo para auditar los registros en la base de datos
@app.get("/usuarios/", response_model=list[schemas.UsuarioResponse])
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return usuarios

# Endpoint protegido que retorna la información del usuario en sesión
@app.get("/auth/me", response_model=schemas.UsuarioResponse)
def leer_usuario_actual(usuario_actual: models.Usuario = Depends(get_usuario_actual)):
    return usuario_actual