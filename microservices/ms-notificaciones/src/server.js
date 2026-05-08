const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
const nodemailer = require('nodemailer');
const db = require('./db'); // para logs

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
const materiasProto = grpc.loadPackageDefinition(materiasPackageDef).agm.periodosmaterias.v1;
const alumnosProto = grpc.loadPackageDefinition(alumnosPackageDef).alumnos;

// instanciar clientes 
const materiasCliente = new materiasProto.PeriodosMateriasService(
    process.env.MS_MATERIAS_URL || 'localhost:50052', 
    grpc.credentials.createInsecure()
);

const alumnosCliente = new alumnosProto.DocentesAlumnosService(
    process.env.MS_ALUMNOS_URL || 'localhost:50053', 
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
                    // Log del fallo en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['bienvenida', alumnoData.email, alumnoId.toString(), 'fallido']
                    ).catch(err => console.error('Error al guardar log de fallo:', err));
                    // Si el correo falló, le decimos a gRPC que hubo un error lógico
                    callback(null, { success: false, error_message: "Error al enviar el correo SMTP" });
                } else {
                    console.log(`-> ÉXITO: Correo despachado con ID: ${info.messageId}`);
                    // Log del éxito en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['bienvenida', alumnoData.email, alumnoId.toString(), 'enviado']
                    ).catch(err => console.error('Error al guardar log de éxito:', err));
                    // Si el correo salió bien, le avisamos a gRPC que la operación fue un éxito total
                    callback(null, { success: true, error_message: "" });
                }
            });
        });
    });
}

function sendBajaNotif(call, callback) {
    const { alumnoId, docenteId } = call.request;
    console.log(`\n[gRPC] Petición de Baja recibida. Buscando datos...`);

    // 1. Obtener datos del Alumno
    alumnosCliente.GetAlumnoById({ id: alumnoId }, (errorAlumno, alumnoData) => {
        if (errorAlumno) {
            console.error("Falló al buscar alumno:", errorAlumno.details);
            return callback(null, { success: false, error_message: "Alumno no encontrado" });
        }

        // 2. Obtener datos del Docente
        alumnosCliente.GetDocenteById({ id: docenteId }, (errorDocente, docenteData) => {
            if (errorDocente) {
                console.error("Falló al buscar docente:", errorDocente.details);
                return callback(null, { success: false, error_message: "Docente no encontrado" });
            }

            // 3. Armar el correo dirigido al docente
            const mailOptions = {
                from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
                to: docenteData.email,
                subject: `Aviso del Sistema: Baja de Alumno - ${alumnoData.nombre}`,
                html: `
                    <h2>Hola Profesor(a) ${docenteData.nombre},</h2>
                    <p>Le notificamos oficialmente que el alumno <b>${alumnoData.nombre}</b> ha procesado su baja de la materia.</p>
                    <p>Este cambio ya se refleja en su concentrado de alumnos.</p>
                `
            };

            // 4. Enviar correo asíncronamente
            transporter.sendMail(mailOptions, (errorEnvio, info) => {
                if (errorEnvio) {
                    console.error("Fallo SMTP en Baja:", errorEnvio);
                    // Log del fallo en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['baja', docenteData.email, docenteId.toString(), 'fallido']
                    ).catch(err => console.error('Error al guardar log de fallo:', err));
                    callback(null, { success: false, error_message: "Error al enviar el correo SMTP" });
                } else {
                    console.log(`-> ÉXITO: Correo de baja notificado al docente. ID: ${info.messageId}`);
                    // Log del éxito en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['baja', docenteData.email, docenteId.toString(), 'enviado']
                    ).catch(err => console.error('Error al guardar log de éxito:', err));
                    callback(null, { success: true, error_message: "" });
                }
            });
        });
    });
}

function sendCierreMateria(call, callback) {
    const { materiaId } = call.request;
    console.log(`\n[gRPC] Petición de Cierre de Materia recibida. Buscando datos...`);

    // 1. Obtener datos de la Materia
    materiasCliente.GetMateriaById({ id: materiaId }, (errorMateria, materiaData) => {
        if (errorMateria) {
            console.error("Falló al buscar materia:", errorMateria.details);
            return callback(null, { success: false, error_message: "Materia no encontrada" });
        }

        // 2. Obtener la lista completa de alumnos inscritos
        alumnosCliente.GetAlumnosByMateria({ materiaId: materiaId }, (errorAlumnos, response) => {
            if (errorAlumnos) {
                console.error("Falló al obtener lista de alumnos:", errorAlumnos.details);
                return callback(null, { success: false, error_message: "Error al consultar lista de alumnos" });
            }

            const alumnos = response.alumnos || [];
            if (alumnos.length === 0) {
                console.log("-> AVISO: La materia se cerró pero no tenía alumnos inscritos.");
                return callback(null, { success: true, error_message: "Sin alumnos a notificar" });
            }

            // Extraer correos y unirlos por comas para el BCC
            const correosBcc = alumnos.map(a => a.email).join(', ');

            // 3. Armar el correo masivo
            const mailOptions = {
                from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
                to: process.env.MAIL_FROM, // Se envía al sistema mismo
                bcc: correosBcc, // Todos los alumnos reciben copia oculta
                subject: `Aviso Académico: Cierre de la materia ${materiaData.nombre}`,
                html: `
                    <h2>Aviso Importante</h2>
                    <p>Estimado alumno, le notificamos que el docente ha cerrado oficialmente la evaluación para la materia: <b>${materiaData.nombre}</b>.</p>
                    <p>Sus calificaciones finales ya han sido publicadas y no están sujetas a más modificaciones.</p>
                    <p>Por favor, ingrese al sistema AGM para revisar su concentrado.</p>
                `
            };

            // 4. Enviar correo asíncronamente
            transporter.sendMail(mailOptions, (errorEnvio, info) => {
                if (errorEnvio) {
                    console.error("Fallo SMTP en Cierre:", errorEnvio);
                    // Log del fallo en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['cierre_materia', correosBcc, materiaId.toString(), 'fallido']
                    ).catch(err => console.error('Error al guardar log de fallo:', err));
                    callback(null, { success: false, error_message: "Error al enviar el correo masivo" });
                } else {
                    console.log(`-> ÉXITO: Correos de cierre enviados a ${alumnos.length} alumnos. ID: ${info.messageId}`);
                    // Log del éxito en la base de datos
                    db.query(
                        'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                        ['cierre_materia', correosBcc, materiaId.toString(), 'enviado']
                    ).catch(err => console.error('Error al guardar log de éxito:', err));
                    callback(null, { success: true, error_message: "" });
                }
            });
        });
    });
}

function sendResetPassword(call, callback) {
    const { email, token } = call.request;
    console.log(`\n[gRPC] Petición de Reset Password recibida para: ${email}`);

    // Asumimos que el frontend de Angular correrá en algún puerto estándar como 4200
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:4200';
    const resetUrl = `${baseUrl}/restablecer?token=${token}`;

    const mailOptions = {
        from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
        to: email,
        subject: `Recuperación de Contraseña - AGM`,
        html: `
            <h2>Recuperación de Acceso</h2>
            <p>Hemos recibido una solicitud para restablecer la contraseña de su cuenta.</p>
            <p>Haga clic en el siguiente enlace seguro para crear una nueva contraseña:</p>
            <a href="${resetUrl}" style="display: inline-block; padding: 10px 20px; background-color: #004b87; color: #ffffff; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a>
            <p><small>Este enlace es de un solo uso y expirará por seguridad. Si no solicitó este cambio, ignore este correo.</small></p>
        `
    };

    transporter.sendMail(mailOptions, (errorEnvio, info) => {
        if (errorEnvio) {
            console.error("Fallo SMTP en Reset Password:", errorEnvio);
            // Log del fallo en la base de datos
            db.query(
                'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                ['reset_password', email, null, 'fallido']
            ).catch(err => console.error('Error al guardar log de fallo:', err));
            callback(null, { success: false, error_message: "Error al enviar el enlace de recuperación" });
        } else {
            console.log(`-> ÉXITO: Correo de recuperación enviado a ${email}. ID: ${info.messageId}`);
            // Log del éxito en la base de datos
            db.query(
                'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                ['reset_password', email, null, 'enviado']
            ).catch(err => console.error('Error al guardar log de éxito:', err));
            callback(null, { success: true, error_message: "" });
        }
    });
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