const amqp = require('amqplib');
const { v4: uuidv4 } = require('uuid');

class RabbitMQRpcClient {
    constructor() {
        this.connection = null;
        this.channel = null;
        this.callbackQueue = null;
        this.url = process.env.RABBITMQ_URL || 'amqp://localhost';
        this.responses = new Map();
    }

    async connect() {
        if (this.connection) return;
        this.connection = await amqp.connect(this.url);
        this.channel = await this.connection.createChannel();
        const q = await this.channel.assertQueue('', { exclusive: true });
        this.callbackQueue = q.queue;

        this.channel.consume(this.callbackQueue, (msg) => {
            const correlationId = msg.properties.correlationId;
            if (this.responses.has(correlationId)) {
                const resolve = this.responses.get(correlationId);
                resolve(JSON.parse(msg.content.toString()));
                this.responses.delete(correlationId);
            }
        }, { noAck: true });
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

            this.channel.sendToQueue(queueName, Buffer.from(payload), {
                correlationId: correlationId,
                replyTo: this.callbackQueue
            });
        });
    }
}

module.exports = new RabbitMQRpcClient();
