# Infraestructura y Persistencia

Este directorio contiene las configuraciones y scripts necesarios para la orquestación, despliegue y mantenimiento de la capa de datos del sistema AGM.

## Componentes de Infraestructura

- **Orquestación (Docker Compose):** Definición centralizada para el despliegue de microservicios, bases de datos y servicios de mensajería en contenedores aislados.
- **Estrategia de Almacenamiento:** Implementación del patrón de base de datos por servicio, garantizando que cada módulo mantenga su propia persistencia lógica independiente.
- **Inicialización de Datos:** Scripts SQL para la creación automática de esquemas, tablas y carga de datos iniciales durante el arranque del sistema.
- **Configuración de Red:** Definición de redes virtuales internas para permitir la comunicación gRPC y RabbitMQ entre servicios.

## Uso y Mantenimiento

Los scripts contenidos en `init.sql` son ejecutados automáticamente por el contenedor de base de datos al ser inicializado por primera vez. Para realizar cambios en el esquema global, se recomienda actualizar los scripts de este directorio y reiniciar los volúmenes correspondientes.
