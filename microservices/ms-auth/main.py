from fastapi import FastAPI

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="MS-1 Auth & Users",
    description="Microservicio de Autenticación para el sistema AGM",
    version="1.0.0"
)

# Creamos nuestro primer endpoint de prueba
@app.get("/")
def read_root():
    return {"mensaje": "El microservicio de Auth está corriendo"}