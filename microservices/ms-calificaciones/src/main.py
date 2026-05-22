
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database import engine, Base, get_db
from src import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS-4 Calificaciones",
    description="Gestión de actividades, notas por Excel y promedios ponderados.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "success": True,
        "data": {"status": "ok"},
        "message": "MS-4 Calificaciones en línea"
    }

@app.post("/actividades", summary="Crear una nueva actividad evaluativa")
def crear_actividad(actividad: schemas.ActividadCreate, db: Session = Depends(get_db)):
    # Validar que la ponderación no sea negativa o absurda
    if actividad.ponderacion <= 0 or actividad.ponderacion > 100:
        raise HTTPException(status_code=400, detail="La ponderación debe estar entre 1 y 100.")

    nueva_actividad = models.Actividad(
        materia_id=actividad.materia_id,
        nombre=actividad.nombre,
        ponderacion=actividad.ponderacion
    )
    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)
    
    return {
        "success": True,
        "data": {
            "actividad_id": nueva_actividad.id,
            "nombre": nueva_actividad.nombre
        },
        "message": "Actividad creada correctamente."
    }

@app.get("/actividades/{materia_id}", summary="Listar actividades de una materia")
def listar_actividades(materia_id: str, db: Session = Depends(get_db)):
    actividades = db.query(models.Actividad).filter(models.Actividad.materia_id == materia_id).all()
    
    # Calcular cuánto porcentaje de la calificación final ya está asignado
    total_ponderacion = sum(act.ponderacion for act in actividades)

    return {
        "success": True,
        "data": {
            "materia_id": materia_id,
            "total_ponderacion_registrada": total_ponderacion,
            "actividades": actividades
        },
        "message": "Actividades obtenidas correctamente."
    }