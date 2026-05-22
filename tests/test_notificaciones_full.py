import grpc
import sys
import os

# Añadimos el path para encontrar los protos generados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import notificaciones_pb2
import notificaciones_pb2_grpc

GRPC_HOST = "localhost:50056"

def test_notificaciones_grpc():
    print("====================================================")
    print("   TESTING MS-NOTIFICACIONES (gRPC Direct)          ")
    print("====================================================\n")

    try:
        channel = grpc.insecure_channel(GRPC_HOST)
        stub = notificaciones_pb2_grpc.NotificacionesServiceStub(channel)

        # 1. Probar Reset Password (No depende de otros microservicios para el mail)
        print("[1] Enviando petición de Reset Password...", end=" ")
        req = notificaciones_pb2.ResetPasswordRequest(
            email="test_user@buap.mx",
            token="secure-token-123"
        )
        res = stub.SendResetPassword(req)
        if res.success:
            print("OK (Correo enviado)")
        else:
            print(f"FAILED ({res.error_message})")

        # 2. Probar Bienvenida (Ojo: Esto llamará por gRPC interno a MS-Auth/MS-Periodos)
        # Si no existen los IDs fallará, pero probamos la conectividad.
        print("[2] Enviando Bienvenida (Integración gRPC)...", end=" ")
        req_welcome = notificaciones_pb2.BienvenidaRequest(
            alumnoId="1",
            materiaId="1",
            claveUnica="TEST-CLAVE"
        )
        res_welcome = stub.SendBienvenida(req_welcome)
        if res_welcome.success:
            print("OK")
        else:
            # Es normal que falle si no hay datos reales, pero validamos que el MS responda
            print(f"RESPUESTA MS: {res_welcome.error_message}")

        print("\n====================================================")
        print("   PRUEBAS DE MS-NOTIFICACIONES FINALIZADAS         ")
        print("====================================================")

    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO gRPC: {e}")

if __name__ == "__main__":
    test_notificaciones_grpc()
