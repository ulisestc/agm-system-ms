# API Gateway

El API Gateway es el punto de entrada centralizado para todas las solicitudes de clientes externos hacia el ecosistema de microservicios de AGM.

## Responsabilidades Principales

- **Enrutamiento de Solicitudes:** Dirige el tráfico entrante hacia el microservicio correspondiente basándose en el prefijo de la URL.
- **Gestión de CORS:** Centraliza las políticas de Cross-Origin Resource Sharing para permitir la comunicación segura con las aplicaciones cliente.
- **Abstracción de Red:** Oculta la topología de la red interna de microservicios, exponiendo una interfaz unificada.
- **Validación de Salud:** Implementa endpoints de health check para monitorear el estado operativo de la puerta de enlace.

## Configuración y Ejecución

1.  Asegúrese de definir las variables de entorno para los hosts de cada microservicio (ej. `MS_AUTH_HOST`, `MS_DOCENTES_HOST`).
2.  Instale las dependencias necesarias: `pip install -r requirements.txt`
3.  Inicie el servicio mediante Uvicorn: `uvicorn main:app --port 80`

## Arquitectura
En entornos de producción, el Gateway utiliza una combinación de Nginx para el manejo eficiente de conexiones y FastAPI para la lógica de proxy dinámico.
