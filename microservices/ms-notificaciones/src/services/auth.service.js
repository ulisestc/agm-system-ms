const rpcClient = require('../clients/rpc_client');

class AuthService {
    async validateToken(token) {
        if (!token) {
            return { valid: false, error_message: "Token no proporcionado" };
        }
        try {
            const response = await rpcClient.call('rpc_auth_queue', 'validate_token', { token });
            return response;
        } catch (error) {
            console.error("[AuthService] Error validando token:", error.message);
            return { valid: false, error_message: "Error de comunicación con Auth" };
        }
    }
}

module.exports = new AuthService();
