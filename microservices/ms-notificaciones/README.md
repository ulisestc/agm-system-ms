# Microservicio de Notificaciones

Este componente actúa como el motor de mensajería asíncrona de la plataforma. Es responsable de despachar comunicaciones transaccionales y alertas a los usuarios.

## Características Principales

- **Comunicaciones de Seguridad:** Envío de enlaces para la recuperación de credenciales de acceso.
- **Notificaciones Transaccionales:** Avisos de bienvenida y confirmaciones de registro.
- **Alertas Operativas:** Distribución de avisos relacionados con procesos académicos (ej. publicación de calificaciones).

## Tecnologías Utilizadas
Desarrollado en **Node.js** para aprovechar su modelo de I/O no bloqueante, ideal para el procesamiento eficiente de colas de envío de correo electrónico.

## Configuración y Ejecución

1.  Instale los paquetes de Node: `npm install`
2.  Configure los parámetros de su proveedor SMTP en el archivo `.env`.
3.  Inicie el proceso: `npm start`
