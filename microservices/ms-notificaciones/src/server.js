
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') }); // variables de entorno

// ruta del contrato grpc
const PROTO_PATH = path.resolve(__dirname, '../../../proto/notificaciones.proto');

// cargar .proto
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,       // Mantener nombres originales
    longs: String,        // Parsear números grandes como strings
    enums: String,
    defaults: true,
    oneofs: true
});

// Cargar el paquete gRPC
const notificacionesProto = grpc.loadPackageDefinition(packageDefinition).notificaciones;

// Los Controladores (Handlers)
// Se definen las funciones definidas en el contrato
function sendBienvenida(call, callback) {
    const { alumnoId, materiaId } = call.request;
    console.log(`[gRPC] Petición recibida: Bienvenida. Alumno: ${alumnoId}, Materia: ${materiaId}`);
    
    // Por ahora, solo simulamos que fue un éxito
    callback(null, { success: true, error_message: "" });
}

function sendBajaNotif(call, callback) {
    const { alumnoId, docenteId } = call.request;
    console.log(`[gRPC] Petición recibida: Baja. Alumno: ${alumnoId}, Docente: ${docenteId}`);
    callback(null, { success: true, error_message: "" });
}

function sendCierreMateria(call, callback) {
    const { materiaId } = call.request;
    console.log(`[gRPC] Petición recibida: Cierre Materia. Materia: ${materiaId}`);
    callback(null, { success: true, error_message: "" });
}

function sendResetPassword(call, callback) {
    const { email, token } = call.request;
    console.log(`[gRPC] Petición recibida: Reset Password. Email: ${email}`);
    callback(null, { success: true, error_message: "" });
}

// Arranque del server gRPC
function main() {
    const server = new grpc.Server();
    
    // Vinculamos el servicio definido en el .proto con nuestras funciones
    server.addService(notificacionesProto.NotificacionesService.service, {
        SendBienvenida: sendBienvenida,
        SendBajaNotif: sendBajaNotif,
        SendCierreMateria: sendCierreMateria,
        sendResetPassword: sendResetPassword
    });

    const port = process.env.GRPC_PORT || '50056';
    const host = `0.0.0.0:${port}`; // puerto grpc
    
    server.bindAsync(host, grpc.ServerCredentials.createInsecure(), (error, port) => {
        if (error) {
            console.error(error);
            return;
        }
        console.log(`Microservicio de Notificaciones escuchando gRPC en ${host}`);
    });
}

main();