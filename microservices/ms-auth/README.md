# Microservicio de Autenticación (Auth)

Este microservicio es responsable de la gestión de identidades, la seguridad perimetral y el control de acceso a la plataforma AGM.

## Características Principales

- **Autenticación:** Validación de credenciales y emisión de tokens JWT para el acceso a recursos protegidos.
- **Gestión de Usuarios:** Registro y administración de cuentas para docentes, alumnos y administradores.
- **Seguridad:** Encriptación de contraseñas mediante algoritmos estándar de la industria (Bcrypt).
- **Recuperación de Acceso:** Flujo de generación y validación de tokens de un solo uso para el restablecimiento de contraseñas.

## Configuración y Ejecución

1.  Copie el archivo de configuración de ejemplo: `cp .env.example .env` y asigne los valores correspondientes.
2.  Instale las dependencias del proyecto: `pip install -r requirements.txt`
3.  Inicie el servidor local: `uvicorn main:app --reload`

El servicio se ejecutará por defecto en el puerto `8000`.

## Endpoints Principales

- `POST /auth/login`: Autenticación y generación de token de acceso.
- `POST /usuarios/`: Creación de un nuevo registro de usuario.
- `GET /auth/me`: Consulta de la información del usuario autenticado actual.
