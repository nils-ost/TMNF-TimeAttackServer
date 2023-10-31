"""
TrachMania Nations Forever - Dedicated Server Reveicer
"""
import signal
import os
import time
import logging
import sys
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.rabbitmq import RabbitMQ

logger = logging.getLogger(__name__)


def graceful_exit(signum, frame):
    raise SystemExit


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level=loglevel)
    logging.getLogger('pika').setLevel(logging.WARNING)
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)
    rabbit = RabbitMQ()
    attached_config = rabbit.request_attachement_from_orchestrator('dreceiver')
    config = get_config('dedicated_run')[attached_config]
    receiver = GbxRemote('host.docker.internal', config['rpc_port'], 'SuperAdmin', config['superadmin_pw'])
    rabbit.send_dedicated_received_message('Dedicated.Disconnected')

    while True:
        delay_counter = 0
        while not receiver.connect():
            if delay_counter == 0:
                logger.info('Waiting for: TMNF - Dedicated Server')
            delay_counter = (delay_counter + 1) % 30
            time.sleep(1)

        logger.info('Connected to: TMNF - Dedicated Server')
        rabbit.send_dedicated_received_message('Dedicated.Connected')

        while True:
            try:
                func, params = receiver.receiveCallback()
                rabbit.send_dedicated_received_message(func, params)
            except SystemExit:
                logger.warning('Received signal to exit...')
                sys.exit(0)
            except ConnectionResetError:
                logger.warning('Lost connection to: TMNF - Dedicated Server')
                rabbit.send_dedicated_received_message('Dedicated.Disconnected')
                break
