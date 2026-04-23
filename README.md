# AGM (Gestión Académica de Calificaciones) - Suite Empresarial

## 🚀 Descripción General
**AGM-Systems** es una plataforma de gestión académica de nivel empresarial diseñada con una **Arquitectura de Microservicios** de alta escalabilidad. El sistema sigue el patrón **Service-per-Database** para garantizar el máximo aislamiento, tolerancia a fallos y escalabilidad independiente de los dominios académicos.

---

## 🏗️ Especificaciones Arquitectónicas

### ¿Por qué Service-per-Database?
El proyecto implementa una estrategia de aislamiento estricto donde cada microservicio posee su propio almacenamiento de datos privado.
* **Soberanía de Datos:** Ningún servicio puede acceder directamente a la base de datos de otro. Todo intercambio de datos ocurre exclusivamente vía gRPC.
* **Escalabilidad Independiente:** Los servicios con altas cargas de escritura (como `ms-grades`) pueden escalarse o migrarse a clusters de bases de datos de alto rendimiento sin afectar a los servicios de bajo tráfico.
* **Arquitectura Evolutiva:** Permite a los equipos actualizar el esquema de la base de datos de un servicio o incluso cambiar el motor de base de datos (ej. de SQL a NoSQL) sin impactar al resto del sistema.
* **Aislamiento de Fallos:** Una corrupción de base de datos o caída en el servicio `ms-attendance` no impedirá que los usuarios inicien sesión a través de `ms-auth`.

### Patrones de Comunicación
| Patrón | Implementación | Propósito |
| :--- | :--- | :--- |
| **Interno (Este-Oeste)** | **gRPC (Protocol Buffers)** | Comunicación binaria de baja latencia y tipado fuerte entre servicios. |
| **Externo (Norte-Sur)** | **REST API** | Interfaz estandarizada para el frontend en Angular a través de un API Gateway. |
| **Service Discovery** | **Docker DNS** | Resolución interna mediante nombres de contenedores para una red resiliente. |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Razón de uso |
| :--- | :--- | :--- |
| **Runtime de Backend** | Node.js (TS) | I/O asíncrono ideal para la orquestación de microservicios. |
| **Framework RPC** | gRPC | Alto rendimiento y desarrollo basado en contratos. |
| **API Gateway** | Express-Gateway / Custom | Gestión de aspectos transversales (Auth, Rate Limiting, Logs). |
| **Base de Datos** | PostgreSQL | Robustez, cumplimiento ACID y aislamiento lógico por esquemas. |
| **Orquestación** | Docker Compose | Entornos de desarrollo y despliegue estandarizados. |
| **Frontend** | Angular 20 | Tipado estricto y modularidad para interfaces empresariales complejas. |

---

## 📁 Estructura del Proyecto

```text
AGM-Systems/
├── microservices/        # Dominios de lógica de negocio
│   ├── ms-auth/          # Gestión de Identidad y Seguridad
│   ├── ms-grades/        # Gestión central de calificaciones
│   └── ... (otros)      # Servicios especializados
├── proto/                # Definiciones de Contratos gRPC (.proto)
├── gateway/              # API Gateway (Traducción REST-a-gRPC)
├── frontend/             # Aplicación Angular 20 SPA
├── infrastructure/       # scripts de Docker e inicialización de DB
└── README.md             # Documentación del sistema
```

---

## 🛰️ Mapa de Servicios y Especificaciones

Cada servicio está diseñado como un contexto delimitado (Bounded Context) independiente.

| Nombre del Servicio | Puerto | Base de Datos | Responsabilidad Principal |
| :--- | :--- | :--- | :--- |
| `ms-auth` | 50051 | `auth_db` | Autenticación, emisión de JWT y permisos RBAC. |
| `ms-periodos`| 50052 | `academic_db` | Gestión de ciclos escolares, semestres y calendarios. |
| `ms-materias` | 50053 | `curriculum_db`| Catálogos de materias, sílabos y requisitos académicos. |
| `ms-calificaciones` | 50054 | `grades_db` | Registro de evaluaciones, cálculo de promedio y auditoría. |
| `ms-asistencias` | 50055 | `tracking_db` | Registro de asistencia y alertas por exceso de faltas. |
| `ms-notificaciones` | 50056 | `notify_db` | Despachador de notificaciones por Email, SMS y Push. |
| `ms-reportes` | 50057 | `reports_db` | Agregación de datos para certificados y generación de PDFs. |

---

## ⚙️ Instalación y Desarrollo

### Requisitos Previos
* Docker y Docker Compose
* Node.js 20+
* Postman (para pruebas gRPC/REST)

### Pasos Iniciales
1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repo>
   cd AGM-Systems
   ```

2. **Configurar el Entorno:**
   Cada microservicio contiene un archivo `.env.example`. Crea un archivo `.env` en cada carpeta.

3. **Lanzar la Suite:**
   ```bash
   docker-compose up -d --build
   ```

4. **Verificar Servicios:**
   Revisa los logs del Gateway para asegurar que todos los clientes gRPC estén conectados correctamente.
