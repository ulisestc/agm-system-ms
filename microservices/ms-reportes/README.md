# Microservicio de Reportes

Este módulo está especializado en la extracción, transformación y presentación de datos. Su propósito es generar la documentación oficial y operativa del sistema.

## Características Principales

- **Generación de Documentos PDF:** Creación de formatos estandarizados (listas de asistencia, boletas) utilizando la librería ReportLab.
- **Exportación de Datos (Excel):** Generación de archivos tabulares mediante OpenPyXL para análisis externo.
- **Concentrados Académicos:** Consolidación de resúmenes por grupo o periodo integrando datos de otros servicios.

## Configuración y Ejecución

1.  Asegúrese de instalar las dependencias, que incluyen librerías para la renderización de PDFs y manipulación de archivos Excel.
2.  Ejecute la aplicación: `uvicorn main:app --port 8007`

## Integración
Este servicio actúa como cliente RPC de RabbitMQ para recopilar dinámicamente los datos necesarios de los microservicios de Docentes, Alumnos y Calificaciones antes de proceder con la generación de documentos.
