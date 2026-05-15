"""
Script de generación de código gRPC para ms-reportes.
Ejecutar UNA SOLA VEZ después de instalar dependencias:

    python generate_grpc.py

Genera en el directorio actual:
  - reportes_pb2.py
  - reportes_pb2_grpc.py

a partir de /proto/reportes.proto (raíz del monorepo).
"""
import subprocess
import sys
import os

PROTO_DIR  = os.path.join("..", "..", "proto")  # relativo a ms-reportes/
PROTO_FILE = "reportes.proto"
OUTPUT_DIR = "."                                 # stubs en el mismo directorio que el código

cmd = [
    sys.executable, "-m", "grpc_tools.protoc",
    f"--proto_path={PROTO_DIR}",
    f"--python_out={OUTPUT_DIR}",
    f"--grpc_python_out={OUTPUT_DIR}",
    os.path.join(PROTO_DIR, PROTO_FILE),
]

print(f"Ejecutando: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("[OK] Código gRPC generado correctamente en:", OUTPUT_DIR)
else:
    print("[ERROR] Error al generar código gRPC:")
    print(result.stderr)
    sys.exit(1)
