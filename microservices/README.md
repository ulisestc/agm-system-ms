# Microservicios del Sistema AGM

Este directorio contiene el núcleo de la lógica de negocio del Sistema AGM, estructurado bajo una arquitectura de microservicios. Cada módulo es independiente, posee su propia persistencia de datos y se comunica con los demás mediante protocolos de mensajería.

## Catálogo de Servicios

### ms-auth
Responsable de la seguridad perimetral, gestión de identidades y emisión de tokens de acceso (JWT). Utiliza FastAPI y PostgreSQL.

### ms-periodos-materias
Administra la estructura temporal y académica. Gestiona los ciclos escolares (periodos) y el catálogo de asignaturas (materias). Desarrollado en Django con PostgreSQL.

### ms-docentes
Gestiona el directorio de personal docente y alumnos. Expone procedimientos RPC sobre RabbitMQ para la resolución rápida de perfiles desde otros microservicios. Utiliza FastAPI y PostgreSQL.

### ms-calificaciones
Controla el proceso de evaluación. Permite la definición de actividades, ponderaciones y el registro de notas. Desarrollado en FastAPI con PostgreSQL.

### ms-asistencias
Sistema de control de asistencia basado en tokens dinámicos. Utiliza Redis para la validación de códigos QR y PostgreSQL para el historial de presencia. Desarrollado en FastAPI.

### ms-notificaciones
Motor de mensajería asíncrona. Procesa colas de RabbitMQ para el envío de correos electrónicos transaccionales. Desarrollado en Node.js.

### ms-reportes
Módulo especializado en la síntesis de información. Genera documentos en formato PDF (ReportLab) y Excel (OpenPyXL), integrando datos de otros servicios mediante RabbitMQ RPC. Desarrollado en FastAPI.

## Estructura de Directorios

Cada microservicio mantiene una estructura interna estándar:
- `src/`: Código fuente de la aplicación.
- `Dockerfile`: Definición de la imagen para el despliegue en contenedores.
- `requirements.txt` o `package.json`: Definición de dependencias.
- `.env.example`: Plantilla de variables de configuración.
- `README.md`: Documentación específica del servicio.

## Comunicación Inter-servicios

- **Eventos (RabbitMQ):** Utilizado para notificaciones asíncronas y propagación de cambios de estado entre servicios.
- **RPC (RabbitMQ):** Utilizado para consultas síncronas entre microservicios (Request-Response) sin dependencias directas de red.
- **REST:** Interfaz expuesta hacia el API Gateway para la interacción con las aplicaciones cliente.

## Requisitos de Ejecución

Para ejecutar un servicio de forma individual fuera del entorno de orquestación (Docker Compose), se requiere:
- Python 3.12+ (para servicios basados en FastAPI/Django).
- Node.js LTS (para el servicio de notificaciones).
- Acceso a las instancias correspondientes de PostgreSQL, Redis y RabbitMQ.
