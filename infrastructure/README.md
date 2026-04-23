# 🏗️ Infraestructura y Orquestación

Este directorio es el "centro de control" que define cómo se despliega, interconecta y persiste todo el ecosistema de **AGM-Systems**.

### Componentes de Infraestructura
- **Orquestación con Docker Compose:** Gestiona el ciclo de vida de los 7 microservicios, el Gateway, el Frontend y las Bases de Datos. Define una red virtual aislada donde los servicios se comunican de forma segura.
- **Estrategia de Persistencia:** Implementa el patrón **Service-per-Database**. Aquí se configuran los volúmenes de Docker para asegurar que los datos de PostgreSQL no se pierdan al reiniciar los contenedores y que cada servicio tenga su propio almacenamiento lógico independiente.
- **Gestión de Configuración:** Centraliza las variables de entorno (`.env`) y los secretos del sistema, permitiendo que la aplicación sea portable entre servidores de desarrollo y producción con cambios mínimos.
- **Scripts de Inicialización:** Contiene las definiciones SQL necesarias para que, al arrancar el sistema por primera vez, todas las bases de datos se creen automáticamente con sus esquemas y datos iniciales requeridos.
- **Redes Internas:** Configura el DNS interno de Docker para permitir que los microservicios se encuentren entre sí usando nombres legibles (ej. `grpc://ms-auth:50051`) en lugar de direcciones IP estáticas.
