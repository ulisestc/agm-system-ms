const apiInstance = require('../config/mailer');
const db = require('../config/database');

class EmailService {
    /**
     * Envía un correo usando la API de Brevo (SDK v5.x)
     * @param {Object} options { to, subject, html, bccList }
     * @param {string} notificationType 
     * @param {string} referenceId 
     */
    async sendMail(options, notificationType, referenceId) {
        try {
            // Parsear MAIL_FROM para extraer Nombre y Email (estrictamente desde env)
            const mailFrom = process.env.MAIL_FROM || "";
            let sender = { email: mailFrom };

            const match = mailFrom.match(/(.*)<(.*)>/);
            if (match) {
                sender.name = match[1].trim();
                sender.email = match[2].trim();
            }

            // Construir el objeto de la petición según SDK v5
            const emailPayload = {
                subject: options.subject,
                htmlContent: options.html,
                sender: sender
            };

            // Configurar destinatarios (solo si hay)
            if (options.to) {
                const recipients = Array.isArray(options.to) ? options.to : [options.to];
                emailPayload.to = recipients.map(email => ({ email }));
            }

            // Configurar copia oculta (solo si hay)
            if (options.bccList && options.bccList.length > 0) {
                emailPayload.bcc = options.bccList.map(email => ({ email }));
            }

            console.log(`[EmailService] Despachando ${notificationType} vía Brevo API (v5)...`);
            
            // Llamada a la API usando el cliente instanciado
            const response = await apiInstance.transactionalEmails.sendTransacEmail(emailPayload);
            
            // En v5 la respuesta viene en response.data
            console.log(`[EmailService] ÉXITO: Correo enviado. ID: ${response.data ? response.data.messageId : 'N/A'}`);
            
            await this.logHistory(notificationType, options.to || "BCC Group", referenceId, 'enviado');
            
            return { success: true, messageId: response.data ? response.data.messageId : null };

        } catch (error) {
            console.error(`[EmailService] Fallo en API Brevo para ${notificationType}:`, error.message);
            
            // Si el error viene de la API, imprimir detalles
            if (error.body) {
                console.error("[EmailService] Detalle del error API:", JSON.stringify(error.body));
            }
            
            await this.logHistory(notificationType, options.to || "BCC Group", referenceId, 'fallido');
            throw error;
        }
    }

    async logHistory(type, recipient, referenceId, status) {
        try {
            const query = 'INSERT INTO historial_correos (tipo_notificacion, destinatario, referencia_id, estado) VALUES ($1, $2, $3, $4)';
            const values = [type, recipient, referenceId ? referenceId.toString() : null, status];
            await db.query(query, values);
        } catch (dbError) {
            console.error("[EmailService] Error en historial BD:", dbError.message);
        }
    }
}

module.exports = new EmailService();
