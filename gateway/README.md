# 🚪 API Gateway (Puerta de Enlace)

El **API Gateway** es el componente crítico que actúa como el único punto de entrada para todos los clientes externos, desacoplando la complejidad de nuestra arquitectura de microservicios del mundo exterior.

### Responsabilidades Críticas
1. **Traducción de Protocolos:** Su función principal es recibir peticiones **HTTP/REST** desde el frontend y traducirlas a llamadas **gRPC** de alto rendimiento hacia los microservicios internos.
2. **Seguridad y Autorización:** Centraliza la validación de tokens JWT. Antes de que una petición llegue a servicios sensibles como `ms-calificaciones`, el Gateway verifica la identidad y los permisos del usuario consultando a `ms-auth`.
3. **Enrutamiento Inteligente:** Dirige el tráfico al microservicio correcto basándose en la URL de la petición, permitiendo que la red interna de microservicios permanezca oculta y protegida.
4. **Agregación de Respuestas:** En ciertos endpoints, el Gateway puede consultar múltiples microservicios (ej. juntar datos de materias y calificaciones) para entregar una respuesta unificada, reduciendo el número de llamadas que debe hacer el cliente.
5. **Políticas de Tráfico:** Implementa Rate Limiting y Logging centralizado para proteger el sistema contra abusos y facilitar la auditoría de peticiones.
