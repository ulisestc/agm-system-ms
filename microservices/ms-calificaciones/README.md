# Microservicio de Calificaciones

Este servicio administra el proceso de evaluación académica. Permite el diseño de esquemas de calificación y el registro sistemático del rendimiento estudiantil.

## Características Principales

- **Gestión de Actividades:** Creación de rúbricas, exámenes, tareas y proyectos.
- **Esquemas de Ponderación:** Configuración del valor porcentual de cada actividad dentro de la calificación final.
- **Registro de Notas:** Captura de calificaciones individuales por estudiante y actividad.
- **Cálculo Automatizado:** Procesamiento de promedios parciales y finales basados en las ponderaciones establecidas.

## Configuración y Ejecución

1.  Verifique la conexión a la instancia de PostgreSQL detallada en su `.env`.
2.  Instale las dependencias: `pip install -r requirements.txt`
3.  Inicie la aplicación: `uvicorn src.main:app --port 8004`

## Dependencias
La generación de actas y boletas finales requiere interacción directa con el Microservicio de Reportes.
