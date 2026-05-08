"""
Script de generación de código gRPC.
Ejecutar UNA SOLA VEZ después de instalar dependencias:

    python generate_grpc.py

Esto genera los archivos:
  - src/grpc_generated/alumnosdocentes_pb2.py
  - src/grpc_generated/alumnosdocentes_pb2_grpc.py

a partir de /proto/alumnosdocentes.proto (raíz del monorepo).
"""
import subprocess
import sys
import os

PROTO_DIR   = os.path.join("..", "..", "proto")  # relativo a ms-docentes/
PROTO_FILE  = "alumnosdocentes.proto"
OUTPUT_DIR  = os.path.join("src", "grpc_generated")

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    print("[OK] Codigo gRPC generado correctamente en:", OUTPUT_DIR)
else:
    print("[ERROR] Error al generar codigo gRPC:")
    print(result.stderr)
    sys.exit(1)
