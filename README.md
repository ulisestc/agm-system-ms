# AGM System - Sistema de Gestión Académica

El Sistema AGM es una plataforma integral basada en una arquitectura de microservicios, diseñada para optimizar y automatizar los procesos operativos y académicos de la institución.

## Arquitectura del Sistema

El sistema está compuesto por módulos independientes que se comunican entre sí para garantizar escalabilidad y alto rendimiento:

*   **Auth:** Gestión de identidades, control de acceso y seguridad (JWT).
*   **Periodos y Materias:** Administración del calendario académico y catálogo de asignaturas.
*   **Docentes y Alumnos:** Registro centralizado de perfiles y datos demográficos de la comunidad.
*   **Calificaciones:** Seguimiento de evaluaciones, ponderaciones y cálculo de promedios.
*   **Asistencias:** Registro de asistencia en tiempo real mediante tokens QR dinámicos.
*   **Notificaciones:** Motor asíncrono para el envío de comunicaciones y alertas por correo electrónico.
*   **Reportes:** Generación de documentos oficiales y exportación de datos (PDF y Excel).
*   **Gateway:** Punto de entrada único (API Gateway) que enruta las peticiones de los clientes al microservicio correspondiente.

## Stack Tecnológico

*   **Backend:** Python (FastAPI, Django) y Node.js.
*   **Almacenamiento:** PostgreSQL (datos relacionales) y Redis (caché y tokens temporales).
*   **Mensajería:** RabbitMQ (comunicación asíncrona mediante eventos y síncrona mediante RPC).
*   **Infraestructura:** Docker, Docker Compose y despliegue en la nube.

## Despliegue Local

Para ejecutar el entorno de desarrollo en su máquina local, es necesario contar con Docker y Docker Compose instalados.

1.  Clone el repositorio en su entorno local.
2.  Configure las variables de entorno copiando los archivos `.env.example` a `.env` en cada directorio correspondiente.
3.  Ejecute el siguiente comando en la raíz del proyecto para construir y levantar los contenedores:
    ```bash
    docker-compose up --build
    ```
4.  El API Gateway estará disponible a través de `http://localhost`.

## Estructura del Repositorio

*   `/microservices`: Código fuente de cada servicio independiente.
*   `/gateway`: Lógica de enrutamiento y proxy de la API.
*   `/frontend`: Aplicación cliente desarrollada en Angular.
*   `/infrastructure`: Scripts de inicialización y configuración de bases de datos.
*   `/postman`: Colecciones y entornos exportados para pruebas de API.
