import pika
import uuid
import json
import os
import logging
import threading
import time

logger = logging.getLogger(__name__)

class RabbitMQManager:
    def __init__(self, url=None):
        self.url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        max_retries = 5
        retry_delay = 5
        for i in range(max_retries):
            try:
                params = pika.URLParameters(self.url)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                logger.info("Conectado a RabbitMQ")
                return
            except Exception as e:
                logger.error(f"Error conectando a RabbitMQ (intento {i+1}/{max_retries}): {e}")
                if i < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

    def publish_event(self, exchange, routing_key, message):
        """Publica un evento asíncrono (Pub/Sub)"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()

            self.channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistente
                )
            )
            logger.info(f"Evento publicado: {routing_key}")
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def publish_to_queue(self, queue_name: str, message: dict):
        """Publica un mensaje directamente a una cola durable (sin exchange)."""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info(f"Job publicado en cola: {queue_name}")
        except Exception as e:
            logger.error(f"Error publicando a cola {queue_name}: {e}")

    def subscribe_to_events(self, exchange, queue_name, routing_keys, callback):
        """Se suscribe a eventos asíncronos"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()

            self.channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
            result = self.channel.queue_declare(queue=queue_name, durable=True)
            queue_name = result.method.queue

            for routing_key in routing_keys:
                self.channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)

            def on_message(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(method.routing_key, message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error en callback de suscripción: {e}")
                    # No hacemos ack si falló para reintentar o manejar según lógica
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=queue_name, on_message_callback=on_message)
            logger.info(f"Suscrito a {routing_keys} en exchange {exchange}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error en suscripción de eventos: {e}")

class RabbitMQRpcClient:
    def __init__(self, url=None):
        self.url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None
        self._connect()

    def _connect(self):
        params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, queue_name, action, data, timeout=10):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        payload = {
            "action": action,
            "data": data
        }

        try:
            if not self.channel or self.channel.is_closed:
                self._connect()

            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(payload))
            
            start_time = time.time()
            while self.response is None:
                self.connection.process_data_events(time_limit=1)
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"RPC Timeout calling {queue_name}:{action}")
            
            return self.response
        except Exception as e:
            logger.error(f"Error en llamada RPC: {e}")
            return {"success": False, "message": str(e)}

class RabbitMQRpcServer:
    def __init__(self, queue_name, url=None):
        self.url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.actions = {}

    def register_action(self, action_name, handler):
        self.actions[action_name] = handler

    def _connect(self):
        params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_request)

    def on_request(self, ch, method, props, body):
        try:
            payload = json.loads(body)
            action = payload.get("action")
            data = payload.get("data")
            
            logger.info(f"RPC Request recibida: {action}")
            
            if action in self.actions:
                response = self.actions[action](data)
            else:
                response = {"success": False, "message": f"Acción desconocida: {action}"}

            ch.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id=props.correlation_id),
                body=json.dumps(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error procesando RPC Request: {e}")
            # En caso de error crítico, podríamos querer enviar una respuesta de error al cliente
            # si tenemos el props.reply_to
            try:
                error_response = {"success": False, "message": str(e)}
                ch.basic_publish(
                    exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(correlation_id=props.correlation_id),
                    body=json.dumps(error_response))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except:
                pass

    def start(self):
        logger.info(f"Iniciando Servidor RPC en cola: {self.queue_name}")
        self._connect()
        self.channel.start_consuming()
