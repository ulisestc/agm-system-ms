from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import json
from datetime import datetime

from src.database import engine, Base, get_db, redis_client
from src import models, schemas

# Crear tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS-5 Asistencias QR",
    description="Gestión de sesiones de 10 min y validación de tokens dinámicos.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"mensaje": "¡MS-5 Asistencias QR en línea!"}

@app.post("/sesiones/iniciar", summary="Inicia una sesión de 10 minutos para una materia")
def iniciar_sesion(req: schemas.IniciarSesionRequest, db: Session = Depends(get_db)):
    redis_key = f"sesion_activa:{req.materia_id}"
    
    # Validar si ya hay una sesión corriendo en Redis
    if redis_client.exists(redis_key):
        raise HTTPException(status_code=400, detail="Ya existe una sesión activa para esta materia.")
    
    # Crear ID de sesión y guardar en Postgres (Historial)
    sesion_id = str(uuid.uuid4())
    nueva_sesion = models.SesionAsistencia(
        id=sesion_id,
        materia_id=req.materia_id,
        docente_id=req.docente_id
    )
    db.add(nueva_sesion)
    db.commit()

    # Guardar en Redis con TTL de 600 segundos (10 minutos)
    sesion_data = {
        "sesion_id": sesion_id,
        "inicio_timestamp": datetime.now().timestamp()
    }
    redis_client.setex(redis_key, 600, json.dumps(sesion_data))

    return {
        "success": True, 
        "message": "Sesión iniciada. Expirará en 10 minutos.", 
        "sesion_id": sesion_id
    }

@app.post("/asistencias/registrar", summary="Registra asistencia mediante escaneo de QR")
def registrar_asistencia(req: schemas.RegistrarAsistenciaRequest, db: Session = Depends(get_db)):
    # Validar Anti-replay (el código no se puede usar 2 veces)
    token_key = f"qr_usado:{req.token_qr}"
    if redis_client.exists(token_key):
        raise HTTPException(status_code=400, detail="Código QR inválido o ya utilizado (Anti-replay).")

    # Verificar si hay sesión activa
    sesion_key = f"sesion_activa:{req.materia_id}"
    sesion_activa_str = redis_client.get(sesion_key)
    
    if not sesion_activa_str:
        raise HTTPException(status_code=404, detail="No hay una sesión activa para esta materia o ya expiró.")
    
    sesion_activa = json.loads(sesion_activa_str)
    tiempo_transcurrido = datetime.now().timestamp() - sesion_activa["inicio_timestamp"]
    
    # Determinar estado de asistencia
    # <= 300 seg (5 mins) = Presente | <= 600 seg (10 mins) = Retardo
    if tiempo_transcurrido <= 300:
        estado = "Presente"
    elif tiempo_transcurrido <= 600:
        estado = "Retardo"
    else:
        raise HTTPException(status_code=400, detail="La sesión ha expirado.")

    # Guardar en Postgres
    nuevo_registro = models.RegistroAsistencia(
        sesion_id=sesion_activa["sesion_id"],
        alumno_id=req.alumno_id,
        materia_id=req.materia_id,
        estado=estado
    )
    db.add(nuevo_registro)
    db.commit()

    # Eliminar el token QR en Redis para que no se re-utilice (se guarda 10 mins por seguridad)
    redis_client.setex(token_key, 600, "usado")

    return {
        "success": True, 
        "message": f"Asistencia registrada con éxito.", 
        "estado": estado
    }