const transporter = require('../config/mailer');
const db = require('../config/database');

class EmailService {
    async sendMail(mailOptions, notificationType, referenceId) {
        return new Promise((resolve, reject) => {
            transporter.sendMail(mailOptions, async (errorEnvio, info) => {
                if (errorEnvio) {
                    console.error(`[EmailService] Fallo SMTP para ${notificationType}:`, errorEnvio);
                    await this.logHistory(notificationType, mailOptions.to || mailOptions.bcc, referenceId, 'fallido');
                    return reject(errorEnvio);
                }
                
                console.log(`[EmailService] ÉXITO: Correo ${notificationType} enviado. ID: ${info.messageId}`);
                await this.logHistory(notificationType, mailOptions.to || mailOptions.bcc, referenceId, 'enviado');
                resolve({ success: true, messageId: info.messageId });
            });
        });
    }

    async logHistory(type, recipient, referenceId, status) {
        try {
            const query = 'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)';
            const values = [type, recipient, referenceId ? referenceId.toString() : null, status];
            await db.query(query, values);
        } catch (dbError) {
            console.error("[EmailService] Error guardando historial:", dbError.message);
        }
    }
}

module.exports = new EmailService();
