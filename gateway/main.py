import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AGM API Gateway")

# Configuración de CORS
origins = [
    "https://agm-system-frontend-joselyn-agm.vercel.app",
    "https://agm-system-frontend-30ytwlq1y-joselyn-agm.vercel.app",
    "https://agm-system-frontend.vercel.app",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapeo de prefijos a hosts (desde variables de entorno)
# Formato esperado: ms-auth (sin puerto, se añade :8000 etc)
SERVICES = {
    "auth": {"host": os.getenv("MS_AUTH_HOST"), "port": 8000},
    "periodos": {"host": os.getenv("MS_PERIODOS_HOST"), "port": 8000},
    "docentes": {"host": os.getenv("MS_DOCENTES_HOST"), "port": 8003},
    "calificaciones": {"host": os.getenv("MS_CALIFICACIONES_HOST"), "port": 8004},
    "asistencias": {"host": os.getenv("MS_ASISTENCIAS_HOST"), "port": 8005},
    "reportes": {"host": os.getenv("MS_REPORTES_HOST"), "port": 8007},
}

client = httpx.AsyncClient()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Gateway is up and running (FastAPI)"}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def proxy(request: Request, service: str, path: str):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Servicio '{service}' no encontrado en el Gateway")

    service_config = SERVICES[service]
    target_host = service_config["host"]
    target_port = service_config["port"]

    if not target_host:
        raise HTTPException(status_code=502, detail=f"Configuración de host faltante para el servicio: {service}")

    # Construir la URL de destino
    # Eliminamos el prefijo /api si viene en la URL original
    url = f"http://{target_host}:{target_port}/{path}"
    
    # Capturar query params
    if request.query_params:
        url += f"?{request.query_params}"

    print(f"--> [Proxy] {request.method} {request.url.path} -> {url}")

    try:
        # Reenviar la petición
        content = await request.body()
        headers = dict(request.headers)
        # Eliminar el host original para evitar problemas de proxy
        headers.pop("host", None)

        response = await client.request(
            method=request.method,
            url=url,
            content=content,
            headers=headers,
            timeout=10.0
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as exc:
        print(f"!! [Proxy Error] {exc}")
        raise HTTPException(status_code=502, detail=f"Error conectando al microservicio {service}: {str(exc)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
