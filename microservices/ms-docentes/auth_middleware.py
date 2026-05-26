import os
import sys

# Asegurar que el directorio raíz del microservicio esté en el path de búsqueda de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from rabbitmq_manager import RabbitMQRpcClient


security = HTTPBearer()

def get_current_user_rpc(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Extrae el token y pregunta a ms-auth por RabbitMQ si es válido.
    """
    token = credentials.credentials
    try:
        rpc_client = RabbitMQRpcClient()
        # Llamada RPC síncrona por software, asíncrona por red
        response = rpc_client.call(
            queue_name='rpc_auth_queue',
            action='validate_token',
            data={'token': token}
        )

        if response and response.get('valid') is True:
            user = response.get('user', {})
            # Retorna el diccionario con {'user_id': 1, 'rol': 'docente', ...}
            return {
                'user_id': user.get('id'),
                'rol': user.get('rol'),
                'email': user.get('email')
            }
        else:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el bus de eventos: {str(e)}")
