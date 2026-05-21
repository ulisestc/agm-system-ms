from pathlib import Path

from grpc_tools import protoc


BASE_DIR = Path(__file__).resolve().parent
PROTO_DIR = BASE_DIR.parents[1] / "proto"


def generate() -> int:
    return protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{PROTO_DIR}",
            f"--python_out={BASE_DIR}",
            f"--grpc_python_out={BASE_DIR}",
            str(PROTO_DIR / "auth.proto"),
            str(PROTO_DIR / "notificaciones.proto"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(generate())
