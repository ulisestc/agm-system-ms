import os
from grpc_tools import protoc

def generate():
    # Directorio de trabajo: ruta del repo relativa a este script
    base_dir = os.path.dirname(__file__)
    proto_dir = os.path.normpath(os.path.join(base_dir, '..', '..', 'proto'))
    out_dir = os.path.join(base_dir, 'src', 'grpc_generated')

    # Asegura que el directorio src/grpc_generated exista
    os.makedirs(out_dir, exist_ok=True)

    # Ejecuta el compilador de protoc
    protoc.main((
        '',
        f'-I{proto_dir}',
        f'--python_out={out_dir}',
        f'--grpc_python_out={out_dir}',
        os.path.join(proto_dir, 'calificaciones.proto'),
    ))

    # Crear __init__.py para que Python reconozca el directorio como paquete
    init_path = os.path.join(out_dir, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            pass

if __name__ == '__main__':
    generate()
