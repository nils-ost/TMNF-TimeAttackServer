import json
import sys
import pika
import subprocess
from datetime import datetime
from helpers.config import get_config
from helpers.rabbitmq import wait_for_connection as mq_wait_for_connection
from helpers.mongodb import challenge_id_get, player_update, player_all, ranking_rebuild, hotseat_player_name_set, get_hotseat_mode
import logging

logger = logging.getLogger(__name__)
periodic_counter = 0


def consume_orchestrator_messages(callback_func, timeout=1):
    """
    callback_func needs to take timeout, func, params, ch, props and delivery_tag as arguments
    """
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    mq_wait_for_connection()
    rabbit_config = get_config('rabbit')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_config['host'], port=rabbit_config['port']))
    channel = connection.channel()
    channel.queue_declare(queue=rabbit_config['queue_orchestrator'])
    try:
        for method, properties, body in channel.consume(
                queue=rabbit_config['queue_orchestrator'], auto_ack=False, exclusive=True, inactivity_timeout=timeout):
            if method is None and properties is None and body is None:
                callback_func(timeout=True, func=None, params=None, ch=channel, props=None, delivery_tag=None)
            else:
                func, params = json.loads(body.decode())
                callback_func(timeout=False, func=func, params=params, ch=channel, props=properties, delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f'{sys._getframe().f_code.co_name} {e} {repr(e)}')
    finally:
        channel.cancel()


def identify_dedicated_server(container_id, dtype):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    container_id = container_id.lower()
    dcmd = 'docker' if int(subprocess.check_output('id -u', shell=True).decode('utf-8').strip()) == 0 else 'sudo docker'
    try:
        container_config = json.loads(subprocess.check_output(f'{dcmd} inspect {container_id}', shell=True).decode('utf-8'))
    except Exception:
        logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}")
        return None
    if len(container_config) == 0:
        logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}")
        return None
    container_config = container_config[0]
    if 'com.docker.compose.service' in container_config['Config'].get('Labels', dict()):
        # seems to be defined in compose using it's service-name as container-name
        container_name = container_config['Config']['Labels']['com.docker.compose.service']
    else:
        # not defined in compose using it's real container-name
        container_name = container_config['Name']
    for k, v in get_config('dedicated').items():
        if v.get('type') == dtype and v.get('container') == container_name:
            return k
    logger.warning(f"{sys._getframe().f_code.co_name} Couldn't identify container {container_id}. {container_name} - {dtype} combo not present in config")
    return None


def periodic_events_function():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    # rebuild rankings
    current_challenge = challenge_id_get(current=True)
    if current_challenge is not None:
        ranking_rebuild(current_challenge)
    # check active players for hotseat-mode
    if get_hotseat_mode():
        ts = int(datetime.now().timestamp())
        one_playing = False
        for p in player_all():
            if p.get('connected'):
                if (ts - p.get('ts', ts)) > 60:
                    player_update(player_id=p.get('_id'), connected=False, ts=ts)
                else:
                    one_playing = True
        if not one_playing:
            hotseat_player_name_set(None)


def messages_callback(timeout, func, params, ch, props, delivery_tag):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if timeout:
        global periodic_counter
        periodic_counter = (periodic_counter + 1) % 5
        if periodic_counter == 0:
            periodic_events_function()
        return
    logger.info(f'{sys._getframe().f_code.co_name} {locals()}')
    if func == 'Dedicated.config_request':
        dedicated_key = identify_dedicated_server(params['container_id'], params['dedicated_type'])
        if dedicated_key is None:
            logger.warning(f'{sys._getframe().f_code.co_name} dedicated_key not resolvable, ignoring request')
            ch.basic_ack(delivery_tag=delivery_tag)
            return
        logger.info(f'{sys._getframe().f_code.co_name} Container identified as: {dedicated_key}')
        ch.basic_publish(exchange='', routing_key=props.reply_to, body=json.dumps({'dedicated': {'ingame_name': 'changed'}}))
    ch.basic_ack(delivery_tag=delivery_tag)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    consume_orchestrator_messages(messages_callback, timeout=1)
