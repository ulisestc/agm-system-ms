-- Crear las bases de datos lógicas para cada microservicio
CREATE DATABASE agm_auth_db;
CREATE DATABASE agm_notificaciones_db;
CREATE DATABASE attendance_db;
CREATE DATABASE agm_docentes_db;
CREATE DATABASE agm_periodos_materias_db;
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

-- conectar a base de datos de docentes y crear tablas
\c agm_docentes_db;

CREATE TABLE docentes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE,
    departamento VARCHAR(200)
);

CREATE TABLE materias_docente (
    id SERIAL PRIMARY KEY,
    docente_id INTEGER NOT NULL REFERENCES docentes(id),
    nrc VARCHAR(20) NOT NULL,
    nombre_materia VARCHAR(200) NOT NULL,
    seccion VARCHAR(10),
    clave VARCHAR(20),
    horario VARCHAR(100),
    CONSTRAINT uq_docente_nrc UNIQUE(docente_id, nrc)
);

CREATE TABLE alumnos (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    nrc VARCHAR(20) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_matricula_nrc UNIQUE(matricula, nrc)
);

-- Crear índices explícitamente si son necesarios
CREATE INDEX ix_docentes_id ON docentes(id);
CREATE INDEX ix_docentes_nombre ON docentes(nombre);
CREATE INDEX ix_docentes_email ON docentes(email);

CREATE INDEX ix_materias_docente_id ON materias_docente(id);
CREATE INDEX ix_materias_docente_nrc ON materias_docente(nrc);

CREATE INDEX ix_alumnos_id ON alumnos(id);
CREATE INDEX ix_alumnos_matricula ON alumnos(matricula);
CREATE INDEX ix_alumnos_nrc ON alumnos(nrc);