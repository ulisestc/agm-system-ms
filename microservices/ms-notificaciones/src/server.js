// src/server.js
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// 1. Ruta relativa hacia tu contrato (subes un nivel, luego a la carpeta proto)
const PROTO_PATH = path.resolve(__dirname, '../../../proto/notificaciones.proto');

// 2. Cargar el archivo .proto
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,       // Mantener nombres originales
    longs: String,        // Parsear números grandes como strings
    enums: String,
    defaults: true,
    oneofs: true
});

// 3. Cargar el paquete gRPC
const notificacionesProto = grpc.loadPackageDefinition(packageDefinition).notificaciones;

// 4. Los Controladores (Handlers)
// Aquí es donde defines qué hace tu MS-6 cuando recibe una petición.
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

// 5. Instanciar y arrancar el servidor
function main() {
    const server = new grpc.Server();
    
    // Vinculamos el servicio definido en el .proto con nuestras funciones
    server.addService(notificacionesProto.NotificacionesService.service, {
        SendBienvenida: sendBienvenida,
        SendBajaNotif: sendBajaNotif,
        SendCierreMateria: sendCierreMateria
    });

    const host = '0.0.0.0:50056'; // Puerto gRPC (ej. 50056)
    
    server.bindAsync(host, grpc.ServerCredentials.createInsecure(), (error, port) => {
        if (error) {
            console.error(error);
            return;
        }
        console.log(`Servidor MS-6 (Notificaciones) escuchando gRPC en ${host}`);
        // 'server.start()' ya no es necesario en las versiones nuevas, bindAsync lo arranca.
    });
}

main();