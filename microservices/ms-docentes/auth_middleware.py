import os
import sys

# Asegurar que el directorio raíz del microservicio esté en el path de búsqueda de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from rabbitmq_manager import RabbitMQManager


security = HTTPBearer()

def get_current_user_rpc(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Extrae el token y pregunta a ms-auth por RabbitMQ si es válido.
    """
    token = credentials.credentials
    try:
        rmq_client = RabbitMQManager()
        # Llamada RPC síncrona por software, asíncrona por red
        response = rmq_client.call_auth(action='validate_token', data={'token': token})

        if response and response.get('status') == 'success':
            # Retorna el diccionario con {'user_id': 1, 'rol': 'docente', ...}
            return response.get('user_data')
        else:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el bus de eventos: {str(e)}")
