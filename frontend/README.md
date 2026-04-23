# 💻 Frontend (Angular 20)

Esta carpeta contiene la capa de presentación de **AGM-Systems**, una Single Page Application (SPA) robusta construida con el framework **Angular 20**.

### Propósito en el Ecosistema
El frontend es el consumidor principal de los servicios académicos. Su diseño está orientado a ofrecer una experiencia fluida y reactiva para administradores, profesores y alumnos.

### Especificaciones de Diseño
- **Comunicación Desacoplada:** El frontend nunca se comunica directamente con los microservicios. Todas las interacciones pasan por el **API Gateway** mediante REST, lo que permite cambiar la infraestructura interna sin romper la interfaz de usuario.
- **Modularidad por Dominio:** La aplicación está dividida en módulos que reflejan los microservicios (Módulo de Calificaciones, Módulo de Asistencia, etc.), facilitando el mantenimiento y la carga perezosa (Lazy Loading) para mejorar el rendimiento.
- **Seguridad en el Cliente:** Implementa interceptores para adjuntar automáticamente tokens de seguridad y manejar errores de sesión de forma centralizada.
- **Visualización de Datos:** Especializado en la representación de datos académicos complejos, utilizando componentes dinámicos para boletas, listas y gráficos de rendimiento escolar.
