const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
const nodemailer = require('nodemailer');

require('dotenv').config({ path: path.resolve(__dirname, '../.env') }); // variables de entorno

//config de mail
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT, 10),
    secure: process.env.SMTP_PORT === '465', 
    auth: process.env.SMTP_USER ? {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    } : undefined, // Si no hay usuario (como en smtp4dev), no usa auth
    ignoreTLS: process.env.SMTP_HOST === 'localhost' 
});

// ruta del contrato(s) grpc
const PROTO_PATH = path.resolve(__dirname, '../../../proto/notificaciones.proto');
const periodosMateriasProtoPath = path.resolve(__dirname, '../../../proto/periodosmaterias.proto');
const alumnosDocentesProtoPath = path.resolve(__dirname, '../../../proto/alumnosdocentes.proto');

// opciones proto
const protoOptions = { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true };

// Cargar el paquete(s) gRPC
const notificacionesPackageDef = protoLoader.loadSync(PROTO_PATH, protoOptions);
const materiasPackageDef = protoLoader.loadSync(periodosMateriasProtoPath, protoOptions);
const alumnosPackageDef = protoLoader.loadSync(alumnosDocentesProtoPath, protoOptions);

// convertir a objetos gRPC
const notificacionesProto = grpc.loadPackageDefinition(notificacionesPackageDef).notificaciones;
const materiasProto = grpc.loadPackageDefinition(materiasPackageDef).materias;
const alumnosProto = grpc.loadPackageDefinition(alumnosPackageDef).alumnos;

// instanciar clientes 
const materiasCliente = new materiasProto.PeriodosMateriasService(
    'localhost:50052', 
    grpc.credentials.createInsecure()
);

const alumnosCliente = new alumnosProto.DocentesAlumnosService(
    'localhost:50053', 
    grpc.credentials.createInsecure()
);


// Los Controladores (Handlers)
// Se definen las funciones definidas en el contrato
function sendBienvenida(call, callback) {
    const { alumnoId, materiaId, claveUnica } = call.request;
    console.log(`\n[gRPC] Petición de Bienvenida recibida. Buscando datos...`);

    // 1. Pedimos los datos del alumno al MS-3
    alumnosCliente.GetAlumnoById({ id: alumnoId }, (errorAlumno, alumnoData) => {
        if (errorAlumno) {
            console.error("Falló al buscar alumno:", errorAlumno.details);
            return callback(null, { success: false, error_message: "No se encontró el alumno" });
        }

        // 2. Si el alumno existe, pedimos los datos de la materia al MS-2
        materiasCliente.GetMateriaById({ id: materiaId }, (errorMateria, materiaData) => {
            if (errorMateria) {
                console.error("Falló al buscar materia:", errorMateria.details);
                return callback(null, { success: false, error_message: "No se encontró la materia" });
            }

            // 3. Armar las opciones del correo usando los datos recuperados de gRPC
            const mailOptions = {
                from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
                to: alumnoData.email,
                subject: `¡Bienvenido a la materia: ${materiaData.nombre}!`,
                html: `
                    <h2>Hola ${alumnoData.nombre}</h2>
                    <p>Tu registro en la materia <b>${materiaData.nombre}</b> ha sido exitoso.</p>
                    <p>Tu clave única de acceso al sistema es: <b>AGM-${claveUnica}</b></p>
                    <p>Por favor, ingresa al portal para cambiarla.</p>
                `
            };

            // 4. Disparar el correo asíncronamente
            transporter.sendMail(mailOptions, (errorEnvio, info) => {
                if (errorEnvio) {
                    console.error("Fallo crítico en Nodemailer:", errorEnvio);
                    // Si el correo falló, le decimos a gRPC que hubo un error lógico
                    callback(null, { success: false, error_message: "Error al enviar el correo SMTP" });
                } else {
                    console.log(`-> ÉXITO: Correo despachado con ID: ${info.messageId}`);
                    // Si el correo salió bien, le avisamos a gRPC que la operación fue un éxito total
                    callback(null, { success: true, error_message: "" });
                }
            });
        });
    });
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
        SendResetPassword: sendResetPassword
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