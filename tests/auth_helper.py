import requests

GATEWAY_URL = "http://localhost"
AUTH_URL = f"{GATEWAY_URL}/api/auth"

def get_token(email="docente@buap.mx", password="password123", role="Docente"):
    """Obtiene un token de acceso para un usuario."""
    res = requests.post(f"{AUTH_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        # Intenta crear el usuario si no existe
        requests.post(f"{AUTH_URL}/usuarios/", json={
            "email": email,
            "password": password,
            "rol": role
        })
        res = requests.post(f"{AUTH_URL}/auth/login", data={"username": email, "password": password})
        if res.status_code == 200:
            return res.json()["access_token"]
    return None

def get_auth_headers(email="docente@buap.mx", password="password123", role="Docente"):
    token = get_token(email, password, role)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
