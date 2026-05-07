import grpc
from concurrent import futures

from django.core.management.base import BaseCommand

import periodos_pb2_grpc

from academic.grpc_service import PeriodosService, grpc_port


class Command(BaseCommand):
    help = "Run the gRPC server for ms-periodos."

    def handle(self, *args, **options):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        periodos_pb2_grpc.add_PeriodosServiceServicer_to_server(PeriodosService(), server)
        server.add_insecure_port(f"[::]:{grpc_port()}")
        server.start()
        self.stdout.write(self.style.SUCCESS(f"gRPC server running on port {grpc_port()}"))
        server.wait_for_termination()
