FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY microservices/ms-asistencias/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/ms-asistencias/src ./src

COPY proto/asistencias.proto .
COPY proto/alumnosdocentes.proto .

RUN python -m grpc_tools.protoc -I. --python_out=./src --grpc_python_out=./src asistencias.proto
RUN python -m grpc_tools.protoc -I. --python_out=./src --grpc_python_out=./src alumnosdocentes.proto

RUN sed -i 's/import asistencias_pb2/from . import asistencias_pb2/g' ./src/asistencias_pb2_grpc.py
RUN sed -i 's/import alumnosdocentes_pb2/from . import alumnosdocentes_pb2/g' ./src/alumnosdocentes_pb2_grpc.py

EXPOSE 8005
EXPOSE 50055

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]