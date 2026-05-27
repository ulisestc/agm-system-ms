import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import bcrypt

# Cargar variables desde .env en la raíz
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Lista de URLs cargadas desde .env
DB_URLS = [
    os.getenv("AUTH_DATABASE_URL"),
    os.getenv("PERIODOS_DATABASE_URL"),
    os.getenv("DOCENTES_DATABASE_URL"),
    os.getenv("CALIFICACIONES_DATABASE_URL"),
    os.getenv("ASISTENCIAS_DATABASE_URL"),
    os.getenv("NOTIFICACIONES_DATABASE_URL"),
    os.getenv("REPORTES_DATABASE_URL")
]
DB_URLS = [url for url in DB_URLS if url] # Filtrar nulos

PASSWORD_PLAIN = "password123"

def reset_and_seed():
    print("🚀 Iniciando limpieza total de las 7 bases de datos...")
    
    # Generar hash de contraseña (formato compatible con FastAPI/ms-auth)
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(PASSWORD_PLAIN.encode('utf-8'), salt).decode('utf-8')

    for url in DB_URLS:
        conn = None
        try:
            conn = psycopg2.connect(url)
            conn.autocommit = True
            cur = conn.cursor()
            
            # Obtener nombre del host para el log
            host = url.split('@')[1].split(':')[0]
            print(f"🧹 Limpiando base de datos en: {host}")

            # 1. Truncar todas las tablas excepto las de migraciones y sistema
            cur.execute("""
                SELECT tablename FROM pg_catalog.pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT IN ('alembic_version', 'django_migrations', 'spatial_ref_sys');
            """)
            tables = cur.fetchall()
            
            if tables:
                table_names = [f'"{t[0]}"' for t in tables]
                truncate_query = f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;"
                cur.execute(truncate_query)
                print(f"   ✅ {len(tables)} tablas vaciadas.")
            else:
                print("   ℹ️ No se encontraron tablas para vaciar.")

            # 2. Si es la tabla de usuarios, sembrar los 3 usuarios base
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'usuarios'")
            if cur.fetchone():
                print("   🌱 Sembrando usuarios en MS-AUTH...")
                users = [
                    ("admin@buap.mx", "ADMIN"),
                    ("profesor@buap.mx", "DOCENTE"),
                    ("alumno@buap.mx", "ALUMNO")
                ]
                for email, rol in users:
                    cur.execute(
                        "INSERT INTO usuarios (email, password_hash, rol) VALUES (%s, %s, %s)",
                        (email, hashed_password, rol)
                    )
                print("   ✅ Usuarios creados correctamente.")

            cur.close()
        except Exception as e:
            print(f"   ❌ Error procesando {url}: {e}")
        finally:
            if conn:
                conn.close()

    print("\n✨ Proceso de reseteo completado exitosamente.")

if __name__ == "__main__":
    reset_and_seed()
