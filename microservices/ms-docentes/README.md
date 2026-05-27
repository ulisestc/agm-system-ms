# Microservicio de Docentes y Alumnos

Este componente funciona como el directorio central de recursos humanos y estudiantiles. Gestiona los datos demográficos y académicos del personal y el alumnado.

## Características Principales

- **Perfiles de Docentes:** Administración de información personal, contacto y especialidades del cuerpo docente.
- **Perfiles de Alumnos:** Registro y mantenimiento del expediente básico de los estudiantes.
- **Sincronización de Datos:** Mantiene la consistencia de la información publicando actualizaciones hacia el resto de la arquitectura mediante eventos de RabbitMQ.

## Configuración y Ejecución

1.  Establezca las variables de entorno en el archivo `.env`.
2.  Instale las dependencias necesarias: `pip install -r requirements.txt`
3.  Ejecute el servicio: `python main.py`

Por defecto, el servicio REST se expone en el puerto `8003`.

## Comunicación Interna
El servicio implementa un servidor RPC sobre RabbitMQ (`rpc_docentes_queue`) que permite a otros microservicios consultar información de perfiles de forma síncrona sin acoplamiento de red directo.
