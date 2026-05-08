-- Crear las bases de datos lógicas para cada microservicio
CREATE DATABASE agm_auth_db;
CREATE DATABASE agm_notificaciones_db;
CREATE DATABASE attendance_db;
CREATE DATABASE agm_docentes_db;
CREATE DATABASE reports_db;

-- conectar a base de datos de notificaciones y crear tabla
\c agm_notificaciones_db;

CREATE TABLE historial_correos (
    id SERIAL PRIMARY KEY,
    tipo_notificacion VARCHAR(50) NOT NULL,
    destinatario VARCHAR(150) NOT NULL,
    referencia_id VARCHAR(50),
    estado VARCHAR(20) NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);