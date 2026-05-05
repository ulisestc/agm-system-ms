from fastapi import FastAPI
from src.database import engine, Base, redis_client

# Crear tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS-5 Asistencias QR",
    description="Gestión de sesiones de 10 min y validación de tokens dinámicos.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    # Prueba de conexión rápida a Redis
    try:
        redis_client.ping()
        redis_status = "Conectado"
    except Exception:
        redis_status = "Desconectado"
        
    return {
        "mensaje": "¡MS-5 Asistencias QR en línea!",
        "redis_status": redis_status
    }