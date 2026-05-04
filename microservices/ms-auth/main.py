from fastapi import FastAPI
# Agregamos las importaciones de la base de datos y modelos
from database import engine, Base
import models

Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="MS-1 Auth & Users",
    description="Microservicio de Autenticación para el sistema AGM",
    version="1.0.0"
)

# Creamos el primer endpoint de prueba
@app.get("/")
def read_root():
    return {"mensaje": "¡El microservicio de Auth está corriendo!"}