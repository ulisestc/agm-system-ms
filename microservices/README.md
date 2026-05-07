# AGM Microservices

Este repositorio contiene dos microservicios del proyecto AGM para Servicios Web:

- `ms-periodos`: CRUD de periodos académicos.
- `ms-materias`: CRUD de materias independientes.

`ms-periodos` expone también un servidor gRPC en el puerto `50051`, y `ms-materias` lo consulta para validar que el `periodo_id` exista antes de crear o actualizar una materia.

Cada servicio tiene su propio proyecto Django, su propia base de datos PostgreSQL y su propio despliegue en Docker.

## Estructura

- `ms-periodos/`
- `ms-materias/`
- `proto/`
- `docker-compose.yml`

## Requisitos

- Docker y Docker Compose
- Python 3.12 si deseas correrlos fuera de Docker

## Configuración local

1. Copia los archivos de ejemplo:

```bash
cp ms-periodos/.env.example ms-periodos/.env
cp ms-materias/.env.example ms-materias/.env
```

2. Si vas a correr con Docker, puedes dejar los valores tal como están en este repositorio porque `docker-compose.yml` sobrescribe la conexión a la base de datos con los nombres de servicio internos.

3. Si vas a correr cada microservicio directamente en tu máquina, cambia `DB_HOST` a `localhost` y usa una instancia propia de PostgreSQL.

## Levantar todo con un comando

```bash
docker compose up --build
```

Servicios expuestos:

- `ms-periodos`: `http://localhost:8001`
- `ms-materias`: `http://localhost:8002`
- `ms-periodos gRPC`: `localhost:50051`

Endpoints de salud:

- `http://localhost:8001/health/`
- `http://localhost:8002/health/`

## Ejecutar sin Docker

### `ms-periodos`

```bash
cd ms-periodos
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8000
```

### `ms-materias`

```bash
cd ms-materias
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8000
```

## Pruebas manuales

### 1. Crear un periodo

```bash
curl -X POST http://localhost:8001/api/periodos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "2026 Primavera",
    "fecha_inicio": "2026-01-10",
    "fecha_fin": "2026-05-30",
    "plan_estudios": "ISC 2026",
    "activo": true
  }'
```

### 2. Listar periodos con paginación

```bash
curl http://localhost:8001/api/periodos/?page=1&limit=10
```

### 3. Obtener el periodo activo

```bash
curl http://localhost:8001/api/periodos/activo/
```

### 4. Activar un periodo por ID

```bash
curl -X POST http://localhost:8001/api/periodos/1/activar/
```

### 5. Crear una materia

Antes de crear una materia, asegúrate de haber creado un periodo válido. `ms-materias` consulta a `ms-periodos` por gRPC y rechazará el registro si el `periodo_id` no existe.

```bash
curl -X POST http://localhost:8002/api/materias/ \
  -H "Content-Type: application/json" \
  -d '{
    "nrc": "12345",
    "nombre": "Servicios Web",
    "seccion": "001",
    "clave": "ISW-302",
    "docente_id": 10,
    "docente_nombre": "Dra. López",
    "horario": "Lunes 10:00-12:00",
    "periodo_id": 1,
    "activo": true
  }'
```

### 6. Filtrar materias por periodo

```bash
curl http://localhost:8002/api/materias/?periodo_id=1
```

### 7. Listar materias con nombre de periodo

```bash
curl http://localhost:8002/api/materias/con-periodo/
```

### 8. Consultar una materia por ID

```bash
curl http://localhost:8002/api/materias/1/
```

### 9. Actualizar una materia

```bash
curl -X PUT http://localhost:8002/api/materias/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "nrc": "12345",
    "nombre": "Servicios Web II",
    "seccion": "001",
    "clave": "ISW-402",
    "docente_id": 10,
    "docente_nombre": "Dra. López",
    "horario": "Lunes 10:00-12:00",
    "periodo_id": 1,
    "activo": true
  }'
```

### 10. Eliminar una materia

```bash
curl -X DELETE http://localhost:8002/api/materias/1/
```

## Pruebas automáticas

Si tienes Django instalado en tu entorno local, puedes correr:

```bash
cd ms-periodos && python manage.py test
cd ../ms-materias && python manage.py test
```

## Notas de arquitectura

- `ms-periodos` y `ms-materias` son procesos distintos.
- Cada servicio usa su propia base de datos.
- La comunicación entre servicios queda preparada para integrar gRPC con los contratos en `proto/`.
