import requests
import uuid
import time

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    print("=== Iniciando Pruebas de MS-Auth (RabbitMQ Integration) ===")

    # 1. Health Check
    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"[1] Health Check: {res.json()}")
        assert res.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Crear un usuario de prueba
    test_email = f"test_{uuid.uuid4().hex[:8]}@buap.mx"
    user_data = {
        "email": test_email,
        "password": "password123",
        "rol": "ALUMNO"
    }
    print(f"\n[2] Creando usuario: {test_email}")
    res = requests.post(f"{BASE_URL}/usuarios/", json=user_data)
    print(f"Status: {res.status_code}, Response: {res.json()}")
    assert res.status_code == 200

    # 3. Login
    print(f"\n[3] Probando Login")
    login_data = {
        "username": test_email,
        "password": "password123"
    }
    res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    token = res.json().get("access_token")
    print(f"Token recibido (primeros 20 caracteres): {token[:20]}...")

    # 4. Forgot Password (Triggers RabbitMQ/gRPC)
    print(f"\n[4] Probando Forgot Password para {test_email}")
    forgot_data = {"email": test_email}
    res = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_data)
    print(f"Status: {res.status_code}, Response: {res.json()}")
    assert res.status_code == 202
    
    # Si RESET_PASSWORD_EXPOSE_TOKEN=true en el .env, tendremos el token aquí
    reset_token = res.json().get("reset_token")
    if reset_token:
        print(f"Token de reset capturado (ExposeToken=True): {reset_token}")
        
        # 5. Reset Password
        print(f"\n[5] Probando Reset Password")
        reset_payload = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        res = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload)
        print(f"Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
        
        # 6. Re-Login con nueva contraseña
        print(f"\n[6] Re-Login con nueva contraseña")
        login_data["password"] = "newpassword123"
        res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200
        print("Login exitoso con nueva contraseña.")
    else:
        print("Token de reset no expuesto (ExposeToken=False). No se puede probar Reset Password automáticamente.")

    print("\n=== Pruebas de MS-Auth completadas con éxito ===")

if __name__ == "__main__":
    test_auth_flow()
