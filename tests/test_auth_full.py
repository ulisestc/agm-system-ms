import requests
import uuid
import sys

BASE_URL = "http://localhost/api/auth"

def test_auth_full():
    print("====================================================")
    print("   TESTING MS-AUTH (Lifecycle Completo)             ")
    print("====================================================\n")

    email = f"user_{uuid.uuid4().hex[:6]}@buap.mx"
    password = "SecurePass123!"

    # 1. Registro de Usuario
    print(f"[1] Registrando nuevo usuario: {email}...", end=" ")
    payload = {
        "email": email,
        "password": password,
        "rol": "ALUMNO"
    }
    res = requests.post(f"{BASE_URL}/usuarios/", json=payload)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        return

    # 2. Intento de Registro Duplicado
    print("[2] Probando validación de correo duplicado...", end=" ")
    res = requests.post(f"{BASE_URL}/usuarios/", json=payload)
    if res.status_code == 400:
        print("OK (Bloqueado correctamente)")
    else:
        print(f"FAILED (Se permitió duplicar: {res.status_code})")

    # 3. Login
    print("[3] Iniciando sesión...", end=" ")
    login_data = {"username": email, "password": password}
    res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if res.status_code == 200:
        token = res.json()["access_token"]
        print("OK (Token obtenido)")
    else:
        print(f"FAILED ({res.status_code})")
        return

    # 4. Obtener perfil actual con Token
    print("[4] Obteniendo perfil con JWT...", end=" ")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if res.status_code == 200:
        print(f"OK (Email: {res.json()['email']}, Rol: {res.json()['rol']})")
    else:
        print(f"FAILED ({res.status_code})")

    # 5. Forgot Password
    print(f"[5] Solicitando recuperación de contraseña para {email}...", end=" ")
    res = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": email})
    if res.status_code == 202:
        print("OK (Aceptado para proceso en segundo plano)")
        reset_token = res.json().get("reset_token") # Solo si RESET_PASSWORD_EXPOSE_TOKEN=true
    else:
        print(f"FAILED ({res.status_code})")
        reset_token = None

    # 6. Reset Password (si el token está disponible)
    if reset_token:
        print("[6] Realizando Reset de contraseña...", end=" ")
        new_pass = "NewSecurePass456!"
        reset_payload = {"token": reset_token, "new_password": new_pass}
        res = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_payload)
        if res.status_code == 200:
            print("OK")
            # 7. Login con nueva contraseña
            print("[7] Probando Login con nueva contraseña...", end=" ")
            login_data["password"] = new_pass
            res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
            if res.status_code == 200:
                print("OK")
            else:
                print(f"FAILED ({res.status_code})")
        else:
            print(f"FAILED ({res.status_code})")
    else:
        print("[6] Reset Password SKIPPED (Token no expuesto)")

    print("\n====================================================")
    print("   PRUEBAS DE MS-AUTH FINALIZADAS                   ")
    print("====================================================")

if __name__ == "__main__":
    test_auth_full()
