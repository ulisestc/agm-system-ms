# Interfaz de Usuario (Frontend)

Capa de presentación del sistema AGM, desarrollada como una Single Page Application (SPA) para ofrecer una experiencia interactiva a los diferentes actores académicos.

## Características del Diseño

- **Arquitectura Basada en Componentes:** Desarrollado sobre Angular, permitiendo la reutilización de elementos de interfaz y una lógica desacoplada.
- **Consumo de API Centralizado:** La comunicación se realiza exclusivamente a través del API Gateway, evitando dependencias directas con los microservicios internos.
- **Gestión de Sesiones:** Implementación de interceptores JWT para la gestión automática de la autenticación en cada solicitud.
- **Diseño Responsivo:** Interfaz adaptada para su uso en múltiples dispositivos, facilitando el acceso a docentes y alumnos desde entornos móviles y de escritorio.

## Integración
El frontend depende de las variables de entorno definidas en el archivo de configuración para apuntar correctamente a la URL del Gateway en entornos de desarrollo o producción.
