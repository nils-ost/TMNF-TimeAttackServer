"""
TrachMania Nations Forever - Dedicated Server Reveicer
"""
import time
import logging
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.rabbitmq import request_attachement_from_orchestrator, send_dedicated_received_message

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    attached_config = request_attachement_from_orchestrator('dreceiver')
    config = get_config('dedicated_run')[attached_config]
    receiver = GbxRemote('host.docker.internal', config['rpc_port'], 'SuperAdmin', config['superadmin_pw'])
    send_dedicated_received_message('Dedicated.Disconnected')

    while True:
        delay_counter = 0
        while not receiver.connect():
            if delay_counter == 0:
                logger.info('Waiting for: TMNF - Dedicated Server')
            delay_counter = (delay_counter + 1) % 30
            time.sleep(1)

        logger.info('Connected to: TMNF - Dedicated Server')
        send_dedicated_received_message('Dedicated.Connected')

        while True:
            try:
                func, params = receiver.receiveCallback()
                send_dedicated_received_message(func, params)
            except ConnectionResetError:
                logger.warning('Lost connection to: TMNF - Dedicated Server')
                send_dedicated_received_message('Dedicated.Disconnected')
                break
