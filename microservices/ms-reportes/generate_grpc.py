"""
Script de generación de código gRPC para ms-reportes.
Ejecutar UNA SOLA VEZ después de instalar dependencias:

    python generate_grpc.py

Genera en el directorio actual:
  - reportes_pb2.py y reportes_pb2_grpc.py (desde reportes.proto)
  - periodosmaterias_pb2.py y periodosmaterias_pb2_grpc.py (desde periodosmaterias.proto)

a partir de /proto/*.proto (raíz del monorepo).
"""
import subprocess
import sys
import os

PROTO_DIR  = os.path.join("..", "..", "proto")  # relativo a ms-reportes/
OUTPUT_DIR = "."                                 # stubs en el mismo directorio que el código

# Proto files a generar
PROTO_FILES = [
    "reportes.proto",
    "periodosmaterias.proto",
    "alumnosdocentes.proto",
    "asistencias.proto",
]

for proto_file in PROTO_FILES:
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={PROTO_DIR}",
        f"--python_out={OUTPUT_DIR}",
        f"--grpc_python_out={OUTPUT_DIR}",
        os.path.join(PROTO_DIR, proto_file),
    ]
    
    print(f"Generando {proto_file}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Error al generar {proto_file}:")
        print(result.stderr)
        sys.exit(1)

print("[OK] Todo el código gRPC generado correctamente en:", OUTPUT_DIR)
