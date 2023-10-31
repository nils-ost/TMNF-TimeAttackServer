from helpers.config import get_config
import os
import sys
import pika
import json
import time
import logging


class RabbitMQ():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = get_config('rabbit')
        self._conn = None
        self._sender = None
        self._consumer = None

    def _start_connection(self):
        if self._conn is None or self._conn.is_closed:
            first = True
            while True:
                try:
                    self._conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.config['host'], port=self.config['port']))
                    self.logger.info('RabbitMQ started ... continue')
                    break
                except Exception:
                    if first:
                        first = False
                        self.logger.warning('RabbitMQ pending ... waiting')
                time.sleep(1)
                self.config = get_config('rabbit')
        if self._sender is None or self._sender.is_closed:
            self._sender = self._conn.channel()
        if self._consumer is None or self._consumer.is_closed:
            self._consumer = self._conn.channel()
        channel = self._conn.channel()
        channel.queue_declare(queue=self.config['queue_orchestrator'])
        channel.queue_declare(queue=self.config['queue_dedicated_received_messages'])
        channel.queue_declare(queue=self.config['queue_dedicated_state_changes'])
        channel.close()

    def get_sender_channel(self):
        self._start_connection()
        return self._sender

    def get_consumer_channel(self):
        self._start_connection()
        return self._consumer

    def get_onetime_channel(self):
        self._start_connection()
        return self._conn.channel()

    def send_dedicated_received_message(self, func, params=None):
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
        channel = self.get_sender_channel()
        channel.basic_publish(exchange='', routing_key=self.config['queue_dedicated_received_messages'], body=json.dumps([func, params]))

    def send_dedicated_state_changes(self, new_state):
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
        channel = self.get_sender_channel()
        channel.basic_publish(exchange='', routing_key=self.config['queue_dedicated_state_changes'], body=new_state)

    def send_orchestrator_message(self, func, params=None):
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
        channel = self.get_sender_channel()
        channel.basic_publish(exchange='', routing_key=self.config['queue_orchestrator'], body=json.dumps([func, params]))

    def consume_dedicated_received_messages(self, callback_func):
        """
        callback_func needs to take func, params, ch and delivery_tag as arguments
        """
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')

        def _callback_func(ch, method, properties, body):
            func, params = json.loads(body.decode())
            callback_func(func=func, params=params, ch=ch, delivery_tag=method.delivery_tag)
        channel = self.get_consumer_channel()
        channel.basic_consume(queue=self.config['queue_dedicated_received_messages'], on_message_callback=_callback_func, auto_ack=False, exclusive=True)
        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()

    def consume_dedicated_state_changes(self, callback_func, timeout=1):
        """
        callback_func needs to take timeout, new_state, ch and delivery_tag as arguments
        """
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
        while True:
            channel = self.get_onetime_channel()
            try:
                for method, properties, body in channel.consume(
                        queue=self.config['queue_dedicated_state_changes'], auto_ack=False, exclusive=True, inactivity_timeout=timeout):
                    if method is None and properties is None and body is None:
                        callback_func(timeout=True, new_state=None, ch=channel, delivery_tag=None)
                    else:
                        callback_func(timeout=False, new_state=body.decode(), ch=channel, delivery_tag=method.delivery_tag)
            except SystemExit:
                self.logger.warning(f'{sys._getframe().f_code.co_name} Received signal to exit...')
                return
            except Exception as e:
                self.logger.warning(f'{sys._getframe().f_code.co_name} Exception {e} {repr(e)} restarting RabbitMQ connection')
            finally:
                channel.cancel()

    def request_attachement_from_orchestrator(self, container_type, timeout=20):
        self.logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')

        channel = self.get_onetime_channel()
        callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue
        container_id = os.environ.get('HOSTNAME', 'localhost')

        channel.basic_publish(
            exchange='',
            routing_key=self.config['queue_orchestrator'],
            properties=pika.BasicProperties(reply_to=callback_queue, expiration=str(int(timeout) * 900)),
            body=json.dumps(['Dcontainer.attach_request', {'container_id': container_id, 'container_type': container_type}]))

        try:
            for method, properties, body in channel.consume(queue=callback_queue, auto_ack=True, exclusive=True, inactivity_timeout=int(timeout)):
                if method is None and properties is None and body is None:
                    self.logger.critical(f'{sys._getframe().f_code.co_name} Orchestrator did not respond to attachement request. Exiting...')
                    sys.exit(1)
                else:
                    return json.loads(body.decode())['dedicated_config']
        except Exception:
            pass
        finally:
            channel.cancel()
