# Microservicio de Periodos y Materias

Este módulo está dedicado a la estructuración del ciclo escolar. Administra el calendario académico y el catálogo oficial de asignaturas de la institución.

## Características Principales

- **Gestión de Periodos:** Creación y configuración de ciclos escolares (ej. Semestre Otoño 2024).
- **Catálogo de Materias:** Mantenimiento de la base de datos de asignaturas disponibles.
- **Asignación Académica:** Vinculación de materias con periodos específicos para habilitar la carga académica.

## Configuración y Ejecución

Este servicio está desarrollado sobre el framework web Django.

1.  Asegúrese de configurar sus credenciales de base de datos en el archivo `.env`.
2.  Instale las dependencias: `pip install -r requirements.txt`
3.  Ejecute las migraciones para preparar el esquema de base de datos: `python manage.py migrate`
4.  Inicie el servidor de desarrollo: `python manage.py runserver 8000`

## Integración
Este servicio publica eventos a través de RabbitMQ para notificar a otros módulos sobre la creación o modificación de periodos y materias.
