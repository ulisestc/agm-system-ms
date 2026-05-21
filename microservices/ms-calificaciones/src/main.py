from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base

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