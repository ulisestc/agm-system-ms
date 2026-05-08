from dataclasses import dataclass

import grpc

import periodos_pb2
import periodos_pb2_grpc


@dataclass(frozen=True)
class PeriodosGrpcConfig:
    host: str
    port: int
    timeout_seconds: float = 5.0


class PeriodosGrpcClient:
    def __init__(self, config: PeriodosGrpcConfig):
        self.config = config

    def _channel(self):
        return grpc.insecure_channel(f"{self.config.host}:{self.config.port}")

    def get_periodo_by_id(self, periodo_id: int):
        channel = self._channel()
        try:
            stub = periodos_pb2_grpc.PeriodosServiceStub(channel)
            return stub.GetPeriodoById(periodos_pb2.PeriodoIdRequest(id=periodo_id), timeout=self.config.timeout_seconds)
        finally:
            channel.close()

    def get_periodo_name_by_id(self, periodo_id: int) -> str:
        response = self.get_periodo_by_id(periodo_id)
        return response.data.nombre if response and response.data else ""


def get_periodos_client_from_settings(settings_module):
    host = getattr(settings_module, "PERIODOS_GRPC_HOST", "localhost")
    port = int(getattr(settings_module, "PERIODOS_GRPC_PORT", 50051))
    timeout_seconds = float(getattr(settings_module, "PERIODOS_GRPC_TIMEOUT", 5.0))
    return PeriodosGrpcClient(PeriodosGrpcConfig(host=host, port=port, timeout_seconds=timeout_seconds))
