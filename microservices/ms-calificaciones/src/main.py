from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import io

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
        "data": {"actividad_id": nueva_actividad.id, "nombre": nueva_actividad.nombre},
        "message": "Actividad creada correctamente."
    }

@app.get("/actividades/{materia_id}", summary="Listar actividades de una materia")
def listar_actividades(materia_id: str, db: Session = Depends(get_db)):
    actividades = db.query(models.Actividad).filter(models.Actividad.materia_id == materia_id).all()
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

@app.post("/actividades/{actividad_id}/calificaciones/excel", summary="Cargar calificaciones desde un archivo Excel")
async def cargar_calificaciones_excel(
    actividad_id: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    actividad_id = actividad_id.strip()
    actividad = db.query(models.Actividad).filter(models.Actividad.id == actividad_id).first()
    
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada.")

    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx)")

    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el Excel. Revisa el formato: {str(e)}")

    df.columns = df.columns.str.lower().str.strip()
    if 'matricula' not in df.columns or 'calificacion' not in df.columns:
        raise HTTPException(status_code=400, detail="El Excel debe contener exactamente las columnas 'matricula' y 'calificacion'.")

    registros = 0
    for index, row in df.iterrows():
        matricula = str(row['matricula']).strip()
        if matricula.endswith('.0'):
            matricula = matricula[:-2]

        valor_nota = float(row['calificacion'])

        calificacion_existente = db.query(models.Calificacion).filter_by(
            actividad_id=actividad_id, alumno_id=matricula
        ).first()

        if calificacion_existente:
            calificacion_existente.valor = valor_nota
        else:
            nueva_calif = models.Calificacion(
                actividad_id=actividad_id, alumno_id=matricula, valor=valor_nota
            )
            db.add(nueva_calif)
        registros += 1

    db.commit()

    return {
        "success": True,
        "data": {"registros_procesados": registros},
        "message": f"Se procesaron {registros} calificaciones correctamente para la actividad '{actividad.nombre}'."
    }

@app.get("/calificaciones/{materia_id}/{alumno_id}/promedio", summary="Calcular promedio ponderado final")
def calcular_promedio_final(materia_id: str, alumno_id: str, db: Session = Depends(get_db)):
    materia_id = materia_id.strip()
    alumno_id = alumno_id.strip()
    
    actividades = db.query(models.Actividad).filter(models.Actividad.materia_id == materia_id).all()
    
    if not actividades:
        raise HTTPException(status_code=404, detail="No hay actividades registradas en esta materia.")

    promedio_ponderado = 0.0
    detalles = []

    for act in actividades:
        calif = db.query(models.Calificacion).filter_by(
            actividad_id=str(act.id), alumno_id=alumno_id
        ).first()

        nota = calif.valor if calif else 0.0
        puntos_ganados = nota * (act.ponderacion / 100)
        promedio_ponderado += puntos_ganados
        
        detalles.append({
            "actividad": act.nombre,
            "ponderacion_maxima": f"{act.ponderacion}%",
            "nota_obtenida": nota,
            "puntos_aportados": round(puntos_ganados, 2)
        })

    promedio_final = round(promedio_ponderado, 2)

    return {
        "success": True,
        "data": {
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "promedio_final": promedio_final,
            "desglose": detalles
        },
        "message": "Promedio calculado correctamente."
    }