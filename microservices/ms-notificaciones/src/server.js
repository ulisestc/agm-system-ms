const path = require('path');
const nodemailer = require('nodemailer');
const amqp = require('amqplib');
const db = require('./db');
const rpcClient = require('./rabbitmq_client');

require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT, 10),
    secure: process.env.SMTP_PORT === '465', 
    auth: process.env.SMTP_USER ? {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    } : undefined,
    ignoreTLS: process.env.SMTP_HOST === 'localhost' 
});

async function sendBienvenida(data, callback) {
    const { alumnoId, materiaId, claveUnica } = data;
    console.log(`\n[Event] Procesando Bienvenida...`);

    try {
        const alumnoResp = await rpcClient.call('rpc_docentes_queue', 'get_alumno_by_id', { id: alumnoId });
        if (!alumnoResp.success) throw new Error("Alumno no encontrado");
        const alumnoData = alumnoResp.data;

        const materiaResp = await rpcClient.call('rpc_periodos_queue', 'get_materia_by_id', { id: materiaId });
        if (!materiaResp.success) throw new Error("Materia no encontrada");
        const materiaData = materiaResp.data;

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

        transporter.sendMail(mailOptions, async (errorEnvio, info) => {
            if (errorEnvio) {
                console.error("Fallo SMTP:", errorEnvio);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['bienvenida', alumnoData.email, alumnoId.toString(), 'fallido']);
                callback(errorEnvio);
            } else {
                console.log(`-> ÉXITO: Correo despachado: ${info.messageId}`);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['bienvenida', alumnoData.email, alumnoId.toString(), 'enviado']);
                callback(null, { success: true });
            }
        });
    } catch (err) {
        console.error("Error en sendBienvenida:", err.message);
        callback(err);
    }
}

async function sendBajaNotif(data, callback) {
    const { alumnoId, docenteId } = data;
    console.log(`\n[Event] Procesando Baja...`);

    try {
        const alumnoResp = await rpcClient.call('rpc_docentes_queue', 'get_alumno_by_id', { id: alumnoId });
        if (!alumnoResp.success) throw new Error("Alumno no encontrado");
        const alumnoData = alumnoResp.data;

        const docenteResp = await rpcClient.call('rpc_docentes_queue', 'get_docente_by_id', { id: docenteId });
        if (!docenteResp.success) throw new Error("Docente no encontrado");
        const docenteData = docenteResp.data;

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

        transporter.sendMail(mailOptions, async (errorEnvio, info) => {
            if (errorEnvio) {
                console.error("Fallo SMTP:", errorEnvio);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['baja', docenteData.email, docenteId.toString(), 'fallido']);
                callback(errorEnvio);
            } else {
                console.log(`-> ÉXITO: Correo de baja enviado. ID: ${info.messageId}`);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['baja', docenteData.email, docenteId.toString(), 'enviado']);
                callback(null, { success: true });
            }
        });
    } catch (err) {
        console.error("Error en sendBajaNotif:", err.message);
        callback(err);
    }
}

async function sendCierreMateria(data, callback) {
    const { materiaId } = data;
    console.log(`\n[Event] Procesando Cierre de Materia...`);

    try {
        const materiaResp = await rpcClient.call('rpc_periodos_queue', 'get_materia_by_id', { id: materiaId });
        if (!materiaResp.success) throw new Error("Materia no encontrada");
        const materiaData = materiaResp.data;

        const alumnosResp = await rpcClient.call('rpc_docentes_queue', 'get_alumnos_by_materia', { materiaId: materiaId });
        const alumnos = alumnosResp.alumnos || [];

        if (alumnos.length === 0) {
            console.log("-> Sin alumnos a notificar.");
            return callback(null, { success: true });
        }

        const correosBcc = alumnos.map(a => a.email).join(', ');

        const mailOptions = {
            from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
            to: process.env.MAIL_FROM,
            bcc: correosBcc,
            subject: `Aviso Académico: Cierre de la materia ${materiaData.nombre}`,
            html: `
                <h2>Aviso Importante</h2>
                <p>Estimado alumno, le notificamos que el docente ha cerrado oficialmente la evaluación para la materia: <b>${materiaData.nombre}</b>.</p>
                <p>Sus calificaciones finales ya han sido publicadas y no están sujetas a más modificaciones.</p>
                <p>Por favor, ingrese al sistema AGM para revisar su concentrado.</p>
            `
        };

        transporter.sendMail(mailOptions, async (errorEnvio, info) => {
            if (errorEnvio) {
                console.error("Fallo SMTP:", errorEnvio);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['cierre_materia', correosBcc, materiaId.toString(), 'fallido']);
                callback(errorEnvio);
            } else {
                console.log(`-> ÉXITO: Correos de cierre enviados. ID: ${info.messageId}`);
                await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                    ['cierre_materia', correosBcc, materiaId.toString(), 'enviado']);
                callback(null, { success: true });
            }
        });
    } catch (err) {
        console.error("Error en sendCierreMateria:", err.message);
        callback(err);
    }
}

async function sendResetPassword(data, callback) {
    const { email, token } = data;
    console.log(`\n[Event] Procesando Reset Password para: ${email}`);

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

    transporter.sendMail(mailOptions, async (errorEnvio, info) => {
        if (errorEnvio) {
            console.error("Fallo SMTP:", errorEnvio);
            await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                ['reset_password', email, null, 'fallido']);
            callback(errorEnvio);
        } else {
            console.log(`-> ÉXITO: Correo de recuperación enviado. ID: ${info.messageId}`);
            await db.query('INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)',
                ['reset_password', email, null, 'enviado']);
            callback(null, { success: true });
        }
    });
}

async function startRabbitMQ() {
    const rabbitUrl = process.env.RABBITMQ_URL || 'amqp://localhost';
    const exchange = 'events_exchange';
    const queue = 'notifications_queue';
    const routingKeys = [
        'auth.reset_password',
        'periodos.materia_cerrada',
        'periodos.bienvenida',
        'docentes.baja'
    ];

    try {
        const connection = await amqp.connect(rabbitUrl);
        const channel = await connection.createChannel();

        await channel.assertExchange(exchange, 'topic', { durable: true });
        await channel.assertQueue(queue, { durable: true });

        for (const key of routingKeys) {
            await channel.bindQueue(queue, exchange, key);
        }

        console.log(`[RabbitMQ] Notificaciones escuchando exchange: ${exchange}`);

        channel.consume(queue, async (msg) => {
            if (msg !== null) {
                try {
                    const routingKey = msg.fields.routingKey;
                    const content = JSON.parse(msg.content.toString());
                    console.log(`[RabbitMQ] Recibido evento: ${routingKey}`);

                    const callback = (err) => {
                        if (err) console.error(`Error procesando ${routingKey}:`, err.message);
                        channel.ack(msg);
                    };

                    switch (routingKey) {
                        case 'periodos.bienvenida':
                            await sendBienvenida(content, callback);
                            break;
                        case 'docentes.baja':
                            await sendBajaNotif(content, callback);
                            break;
                        case 'periodos.materia_cerrada':
                            await sendCierreMateria(content, callback);
                            break;
                        case 'auth.reset_password':
                            await sendResetPassword(content, callback);
                            break;
                        default:
                            console.warn(`Evento desconocido: ${routingKey}`);
                            channel.ack(msg);
                    }
                } catch (parseError) {
                    console.error("Error parseando mensaje:", parseError);
                    channel.nack(msg, false, false);
                }
            }
        });

    } catch (error) {
        console.error("Fallo al conectar RabbitMQ:", error.message);
        setTimeout(startRabbitMQ, 5000);
    }
}

async function main() {
    console.log("Microservicio de Notificaciones iniciado");
    await startRabbitMQ();
}

main();
