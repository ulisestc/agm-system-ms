from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import threading
import uuid
import json
from datetime import datetime

from src.database import engine, Base, get_db, redis_client
from src import grpc_server
from src import models, schemas
from src.grpc_client import validar_alumno_en_materia

# Crear tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS-5 Asistencias QR",
    description="Gestión de sesiones de 10 min y validación de tokens dinámicos.",
    version="1.0.0"
)

# Configuración de CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "success": True,
        "data": {"mensaje": "¡MS-5 Asistencias QR en línea!"},
        "message": "Conexión exitosa"
    }

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
        "data": {"sesion_id": sesion_id},
        "message": "Sesión iniciada. Expirará en 10 minutos."
    }

@app.post("/asistencias/registrar", summary="Registra asistencia mediante escaneo de QR")
def registrar_asistencia(req: schemas.RegistrarAsistenciaRequest, db: Session = Depends(get_db)):
    # Validar Anti-replay (el código no se puede usar 2 veces)
    token_key = f"qr_usado:{req.token_qr}"
    if redis_client.exists(token_key):
        raise HTTPException(status_code=400, detail="Código QR inválido o ya utilizado (Anti-replay).")

    # Consultar al MS-3 (Docentes) si el alumno pertenece a la materia
    esta_inscrito = validar_alumno_en_materia(req.alumno_id, req.materia_id)
    if not esta_inscrito:
        raise HTTPException(
            status_code=403, 
            detail=f"El alumno {req.alumno_id} no está inscrito en la materia {req.materia_id}."
        )
    # ----------------------------

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
        "data": {"estado": estado},
        "message": "Asistencia registrada con éxito."
    }

@app.delete("/sesiones/{materia_id}/cerrar", summary="Cierra forzosamente una sesión activa")
def cerrar_sesion(materia_id: str, db: Session = Depends(get_db)):
    sesion_key = f"sesion_activa:{materia_id}"
    
    if not redis_client.exists(sesion_key):
        raise HTTPException(status_code=404, detail="No hay una sesión activa para esta materia.")
    
    # Obtener el ID antes de borrar
    sesion_data = json.loads(redis_client.get(sesion_key))
    sesion_id = sesion_data["sesion_id"]
    
    # Eliminar de Redis (cierre forzoso)
    redis_client.delete(sesion_key)
    
    # Actualizar estado en Postgres
    db_sesion = db.query(models.SesionAsistencia).filter(models.SesionAsistencia.id == sesion_id).first()
    if db_sesion:
        db_sesion.activa = False
        db.commit()

    return {
        "success": True, 
        "data": {},
        "message": "Sesión cerrada correctamente."
    }

@app.get("/asistencias/{materia_id}/hoy", summary="Obtiene los alumnos que han registrado asistencia en la sesión actual")
def asistencias_hoy(materia_id: str, db: Session = Depends(get_db)):
    # Buscar la sesión más reciente de esta materia en Postgres
    sesion_reciente = db.query(models.SesionAsistencia).filter(
        models.SesionAsistencia.materia_id == materia_id
    ).order_by(models.SesionAsistencia.fecha_creacion.desc()).first()
    
    if not sesion_reciente:
        return {"success": True, "data": [], "message": "No hay sesiones registradas hoy."}
        
    registros = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.sesion_id == sesion_reciente.id
    ).all()
    
    return {
        "success": True, 
        "data": {
            "sesion_id": sesion_reciente.id,
            "fecha": sesion_reciente.fecha_creacion,
            "registros": registros
        },
        "message": "Asistencias de la sesión más reciente obtenidas."
    }

@app.get("/asistencias/{materia_id}/historial", summary="Obtiene el historial de sesiones pasadas de una materia")
def historial_asistencias(
    materia_id: str, 
    page: int = Query(1, ge=1, description="Número de página"), 
    limit: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"), 
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    
    total_sesiones = db.query(models.SesionAsistencia).filter(
        models.SesionAsistencia.materia_id == materia_id
    ).count()
    
    sesiones = db.query(models.SesionAsistencia).filter(
        models.SesionAsistencia.materia_id == materia_id
    ).order_by(models.SesionAsistencia.fecha_creacion.desc()).offset(offset).limit(limit).all()
    
    return {
        "success": True, 
        "data": {
            "total_records": total_sesiones,
            "current_page": page,
            "limit": limit,
            "total_pages": (total_sesiones + limit - 1) // limit,
            "sesiones": sesiones
        },
        "message": "Historial paginado obtenido correctamente."
    }

def _start_grpc():
    try:
        grpc_server.serve()
    except Exception as e:
        print(f"[WARNING] No se pudo iniciar el servidor gRPC: {e}")


# Evento de inicio de FastAPI para arrancar el servidor gRPC en segundo plano
@app.on_event("startup")
def startup_event():
    grpc_thread = threading.Thread(target=_start_grpc, daemon=True)
    grpc_thread.start()