import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AGM API Gateway")

# Configuración de CORS alineada con microservicios
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapeo de prefijos a hosts
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
    return {"status": "ok", "message": "Gateway FastAPI is RUNNING", "port": os.getenv("PORT", "80")}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def catch_all(request: Request, path: str):
    # Analizar el path para extraer el servicio
    # Casos esperados: 
    # 1. /api/auth/login -> service='auth', subpath='login'
    # 2. /auth/login     -> service='auth', subpath='login'
    
    parts = path.strip("/").split("/")
    if not parts or parts[0] == "":
        return {"message": "AGM Gateway Root"}
        
    if parts[0] == "api":
        if len(parts) < 2:
            raise HTTPException(status_code=404, detail="Debe especificar un servicio tras /api/")
        service = parts[1]
        subpath = "/".join(parts[2:])
    else:
        service = parts[0]
        subpath = "/".join(parts[1:])

    return await handle_proxy(request, service, subpath)

async def handle_proxy(request: Request, service: str, path: str):
    if service not in SERVICES:
        print(f"!! [Proxy Error] Servicio '{service}' no encontrado en SERVICES (Path original: {request.url.path})")
        raise HTTPException(status_code=404, detail=f"Servicio '{service}' no encontrado")

    service_config = SERVICES[service]
    target_host = service_config["host"]
    target_port = service_config["port"]

    if not target_host:
        print(f"!! [Proxy Error] Host faltante para: {service}")
        raise HTTPException(status_code=502, detail=f"Host faltante para: {service}")

    url = f"http://{target_host}:{target_port}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"

    print(f"--> [Proxy] {request.method} /{service}/{path} -> {url}")

    try:
        content = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)

        response = await client.request(
            method=request.method,
            url=url,
            content=content,
            headers=headers,
            timeout=15.0
        )

        resp_headers = dict(response.headers)
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-credentials",
            "access-control-allow-methods",
            "access-control-allow-headers",
            "access-control-expose-headers"
        ]
        for h in cors_headers:
            resp_headers.pop(h, None)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=resp_headers
        )
    except Exception as e:
        print(f"!! [Proxy Error] {str(e)}")
        raise HTTPException(status_code=502, detail=f"Error conectando a {service}: {str(e)}")
