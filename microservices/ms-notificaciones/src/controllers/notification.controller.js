const emailService = require('../services/email.service');

class NotificationController {
    async handleRetardo(data) {
        const { alumno_id, materia_id, sesion_id, timestamp } = data;
        const alertEmail = process.env.ALERT_EMAIL || process.env.MAIL_FROM;

        const mailOptions = {
            from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
            to: alertEmail,
            subject: `Alerta de Retardo - Alumno ${alumno_id}`,
            html: `
                <h2>Alerta de Retardo</h2>
                <p>Se registró un retardo en la materia <b>${materia_id}</b>.</p>
                <p><b>Alumno:</b> ${alumno_id}</p>
                <p><b>Sesión:</b> ${sesion_id}</p>
                <p><b>Fecha y hora:</b> ${timestamp}</p>
            `
        };

        return await emailService.sendMail(mailOptions, 'retardo', sesion_id || alumno_id || null);
    }

    async handleBienvenida(data) {
        const { alumnoNombre, alumnoEmail, alumnoId, materiaNombre, claveUnica } = data;
        
        const mailOptions = {
            from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
            to: alumnoEmail,
            subject: `¡Bienvenido a la materia: ${materiaNombre}!`,
            html: `
                <h2>Hola ${alumnoNombre}</h2>
                <p>Tu registro en la materia <b>${materiaNombre}</b> ha sido exitoso.</p>
                <p>Tu clave única de acceso al sistema es: <b>AGM-${claveUnica}</b></p>
                <p>Por favor, ingresa al portal para cambiarla.</p>
            `
        };

        return await emailService.sendMail(mailOptions, 'bienvenida', alumnoId);
    }

    async handleBaja(data) {
        const { alumnoNombre, docenteNombre, docenteEmail, docenteId } = data;

        const mailOptions = {
            from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
            to: docenteEmail,
            subject: `Aviso del Sistema: Baja de Alumno - ${alumnoNombre}`,
            html: `
                <h2>Hola Profesor(a) ${docenteNombre},</h2>
                <p>Le notificamos oficialmente que el alumno <b>${alumnoNombre}</b> ha procesado su baja de la materia.</p>
                <p>Este cambio ya se refleja en su concentrado de alumnos.</p>
            `
        };

        return await emailService.sendMail(mailOptions, 'baja', docenteId);
    }

    async handleCierreMateria(data) {
        const { materiaId, materiaNombre, alumnosEmails } = data;

        if (!alumnosEmails || alumnosEmails.length === 0) {
            console.log("-> Sin alumnos a notificar del cierre de materia.");
            return { success: true, message: "No recipients" };
        }

        const correosBcc = Array.isArray(alumnosEmails) ? alumnosEmails.join(', ') : alumnosEmails;

        const mailOptions = {
            from: process.env.MAIL_FROM || '"AGM Sistema" <noreply@agm.buap.mx>',
            to: process.env.MAIL_FROM,
            bcc: correosBcc,
            subject: `Aviso Académico: Cierre de la materia ${materiaNombre}`,
            html: `
                <h2>Aviso Importante</h2>
                <p>Estimado alumno, le notificamos que el docente ha cerrado oficialmente la evaluación para la materia: <b>${materiaNombre}</b>.</p>
                <p>Sus calificaciones finales ya han sido publicadas y no están sujetas a más modificaciones.</p>
                <p>Por favor, ingrese al sistema AGM para revisar su concentrado.</p>
            `
        };

        return await emailService.sendMail(mailOptions, 'cierre_materia', materiaId);
    }

    async handleResetPassword(data) {
        const { email, token } = data;
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

        return await emailService.sendMail(mailOptions, 'reset_password', null);
    }
}

module.exports = new NotificationController();
