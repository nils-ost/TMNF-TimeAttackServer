"""
TrachMania Nations Forever - Dedicated Server Reveicer
"""
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.rabbitmq import send_dedicated_received_message
import time


if __name__ == '__main__':
    config = get_config('tmnf-server')
    receiver = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    send_dedicated_received_message('Dedicated.Disconnected')

    while True:
        delay_counter = 0
        while not receiver.connect():
            if delay_counter == 0:
                print('Waiting for: TMNF - Dedicated Server')
            delay_counter = (delay_counter + 1) % 30
            time.sleep(1)

        print('Connected to: TMNF - Dedicated Server')
        send_dedicated_received_message('Dedicated.Connected')

        while True:
            try:
                func, params = receiver.receiveCallback()
                send_dedicated_received_message(func, params)
            except ConnectionResetError:
                print('Lost connection to: TMNF - Dedicated Server')
                send_dedicated_received_message('Dedicated.Disconnected')
                break
