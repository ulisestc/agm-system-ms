const amqp = require('amqplib');
const { v4: uuidv4 } = require('uuid');

class RabbitMQRpcClient {
    constructor() {
        this.connection = null;
        this.channel = null;
        this.callbackQueue = null;
        this.url = process.env.RABBITMQ_URL || 'amqp://localhost';
        this.responses = new Map();
        this.connectPromise = null;
    }

    async connect() {
        if (this.connection && this.channel && this.callbackQueue) return;
        
        if (this.connectPromise) return this.connectPromise;

        this.connectPromise = (async () => {
            try {
                console.log('[RabbitMQRpcClient] Connecting to RabbitMQ...');
                this.connection = await amqp.connect(this.url);
                
                this.connection.on('error', (err) => {
                    console.error('[RabbitMQRpcClient] Connection error:', err.message);
                    this.cleanup();
                });

                this.connection.on('close', () => {
                    console.log('[RabbitMQRpcClient] Connection closed');
                    this.cleanup();
                });

                this.channel = await this.connection.createChannel();
                
                // Usar una cola exclusiva autogenerada
                const q = await this.channel.assertQueue('', { exclusive: true });
                this.callbackQueue = q.queue;

                this.channel.consume(this.callbackQueue, (msg) => {
                    if (!msg) return;
                    const correlationId = msg.properties.correlationId;
                    if (this.responses.has(correlationId)) {
                        const resolve = this.responses.get(correlationId);
                        try {
                            resolve(JSON.parse(msg.content.toString()));
                        } catch (e) {
                            console.error("[RabbitMQRpcClient] Error parseando respuesta RPC:", e.message);
                        }
                        this.responses.delete(correlationId);
                    }
                }, { noAck: true });
                
                console.log(`[RabbitMQRpcClient] RPC Client ready on queue: ${this.callbackQueue}`);
            } catch (error) {
                console.error('[RabbitMQRpcClient] Connection failed:', error.message);
                this.cleanup();
                throw error;
            } finally {
                this.connectPromise = null;
            }
        })();

        return this.connectPromise;
    }

    cleanup() {
        this.connection = null;
        this.channel = null;
        this.callbackQueue = null;
        this.connectPromise = null;
    }

    async call(queueName, action, data, timeout = 10000) {
        await this.connect();
        const correlationId = uuidv4();
        const payload = JSON.stringify({ action, data });

        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.responses.delete(correlationId);
                reject(new Error(`RPC Timeout calling ${queueName}:${action}`));
            }, timeout);

            this.responses.set(correlationId, (res) => {
                clearTimeout(timer);
                resolve(res);
            });

            try {
                this.channel.sendToQueue(queueName, Buffer.from(payload), {
                    correlationId: correlationId,
                    replyTo: this.callbackQueue
                });
            } catch (error) {
                clearTimeout(timer);
                this.responses.delete(correlationId);
                reject(error);
            }
        });
    }
}

module.exports = new RabbitMQRpcClient();
