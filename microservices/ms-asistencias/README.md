# Microservicio de Asistencias

Este módulo optimiza el control de asistencia a través de un sistema de validación basado en códigos QR dinámicos y temporales.

## Características Principales

- **Gestión de Sesiones:** Apertura y cierre de sesiones de clase por parte del personal docente.
- **Generación de Tokens:** Creación de identificadores criptográficos efímeros (QR) para validar la presencia física.
- **Procesamiento en Tiempo Real:** Registro inmediato de la asistencia al escanear el token desde el cliente.
- **Auditoría:** Consulta de historiales de asistencia por materia, periodo o alumno.

## Requisitos de Infraestructura

Para garantizar la rápida expiración y validación de los tokens QR, este servicio depende estrictamente de **Redis** como almacén de datos en memoria.

## Configuración y Ejecución

1.  Configure la variable `REDIS_URL` y la conexión a PostgreSQL en su archivo `.env`.
2.  Instale las dependencias requeridas.
3.  Inicie el servicio: `uvicorn src.main:app --port 8005`
