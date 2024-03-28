"""
TrachMania Nations Forever - Dedicated Server Reveicer
"""
import signal
import os
import time
from helpers.logging import setup_logging
import logging
import sys
from elements import Config
from helpers.GbxRemote import GbxRemote
from helpers.rabbitmq import RabbitMQ

logger = logging.getLogger(__name__)


def graceful_exit(signum, frame):
    raise SystemExit


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    setup_logging('Dedicated - Receiver', loglevel)
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)
    rabbit = RabbitMQ()
    attached_config = rabbit.request_attachement_from_orchestrator('dreceiver')
    rabbit.attach_config(attached_config)
    config = Config.get('dedicated_run')['content'][attached_config]
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
