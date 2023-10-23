import pika
import os
import sys
import json
import time
import logging

logger = logging.getLogger(__name__)
rabbit_config = dict()
mq_connection = None
mq_channel = None


def _get_channel():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global mq_connection
    global mq_channel
    global rabbit_config
    if mq_connection is None:
        first = True
        rabbit_config['host'] = os.environ.get('RABBIT_HOST', 'rabbitmq')
        rabbit_config['port'] = int(os.environ.get('RABBIT_PORT', 5672))
        rabbit_config['queue_orchestrator'] = os.environ.get('RABBIT_QUEUE', 'tas_orchestrator')
        while True:
            try:
                mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_config['host'], port=rabbit_config['port']))
                logger.info('RabbitMQ started ... continue')
                break
            except Exception:
                if first:
                    first = False
                    logger.warning('RabbitMQ pending ... waiting')
            time.sleep(1)
    if mq_channel is None:
        mq_channel = mq_connection.channel()
        mq_channel.queue_declare(queue=rabbit_config['queue_orchestrator'])
    return mq_channel


def ask_orchestrator_whoami(timeout=20):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global rabbit_config
    channel = _get_channel()
    callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue

    channel.basic_publish(
        exchange='',
        routing_key=rabbit_config['queue_orchestrator'],
        properties=pika.BasicProperties(reply_to=callback_queue, expiration=str(int(timeout) * 900)),
        body=json.dumps(['Dedicated.whoami', {}]))

    try:
        for method, properties, body in channel.consume(queue=callback_queue, auto_ack=True, exclusive=True, inactivity_timeout=int(timeout)):
            if method is None and properties is None and body is None:
                logger.critical('orchestrator did not respond to whoami request! exiting...')
                sys.exit(1)
            else:
                return
    except Exception:
        pass
    finally:
        channel.cancel()


def ask_orchestrator_for_config(callback_func, container_id, dedicated_type, current_config, timeout=20):
    """
    callback_func needs to take timeout, config as arguments
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    global rabbit_config
    channel = _get_channel()
    callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue

    channel.basic_publish(
        exchange='',
        routing_key=rabbit_config['queue_orchestrator'],
        properties=pika.BasicProperties(reply_to=callback_queue, expiration=str(int(timeout) * 900)),
        body=json.dumps(['Dedicated.config_request', {'container_id': container_id, 'dedicated_type': dedicated_type, 'current_config': current_config}]))

    try:
        for method, properties, body in channel.consume(queue=callback_queue, auto_ack=True, exclusive=True, inactivity_timeout=int(timeout)):
            if method is None and properties is None and body is None:
                callback_func(timeout=True, config=None)
            else:
                callback_func(timeout=False, config=json.loads(body.decode()))
            break
    except Exception:
        pass
    finally:
        channel.cancel()
