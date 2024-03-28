"""
TrachMania Nations Forever - Dedicated Server Controller
"""
from helpers.logging import setup_logging
from elements import Config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import challenge_get, challenge_update, challenge_id_set
from helpers.mongodb import set_tmnfd_name
from helpers.tmnfd import isPreStart, isPostEnd, prepareChallenges, prepareNextChallenge, kickAllPlayers
from helpers.rabbitmq import RabbitMQ
import signal
import os
import time
import hashlib
import random
import logging

logger = logging.getLogger(__name__)
sender = None
attached_config = None
pre_start_executed = False
post_end_executed = False
dedicated_connected = False


def controller_function(timeout, new_state, ch, delivery_tag):
    global sender
    global attached_config
    global dedicated_connected
    global pre_start_executed
    global post_end_executed

    if not timeout:
        if new_state == 'disconnected':
            dedicated_connected = False
        elif new_state == 'connected':
            while not sender.connect():
                time.sleep(1)
            logger.info('Connected to: TMNF - Dedicated Server')
            dedicated_connected = True
            prepareChallenges(sender, server=attached_config)

            server_name = sender.callMethod('GetServerName')[0]
            set_tmnfd_name(server_name)
            logger.info(f'TMNF - Dedicated Server Name: {server_name}')
            if not isPreStart() and not isPostEnd():
                current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
                challenge_update(current_challenge['UId'], attached_config, force_inc=False)
                logger.info(f"Challenge current: {current_challenge['Name']}")
                challenge_id_set(current_challenge['UId'], on_server=attached_config, current=True)
                prepareNextChallenge(sender, attached_config)
        ch.basic_ack(delivery_tag=delivery_tag)

    elif dedicated_connected:
        if isPreStart() and not pre_start_executed:
            logger.info('Initializing pre start phase')
            # hide the server
            sender.callMethod('SetHideServer', 1)
            # set a password for server
            random.seed(time.time())
            rndpassword = hashlib.md5(str(random.randrange(int(time.time()))).encode('UTF-8')).hexdigest()
            sender.callMethod('SetServerPassword', rndpassword)
            sender.callMethod('SetServerPasswordForSpectator', rndpassword)
            sender.callMethod('SetRefereePassword', rndpassword)
            # kick all players
            kickAllPlayers(sender, 'Tournament not yet started!')
            # clear current and next challenge
            challenge_id_set(None, on_server=attached_config, current=True)
            challenge_id_set(None, on_server=attached_config, next=True)
            # remove all challenges from playlist except the first
            starting_index = 0
            infos_returned = 10
            c_FileNames = list()
            while True:
                for challenge in sender.callMethod('GetChallengeList', infos_returned, starting_index)[0]:
                    c_FileNames.append(challenge['FileName'])
                if len(c_FileNames) % infos_returned == 0:
                    starting_index += infos_returned
                else:
                    break
            if len(c_FileNames) > 1:
                for fn in c_FileNames[1:]:
                    sender.callMethod('RemoveChallenge', fn)
            # start "endless" challenge
            sender.callMethod('SetTimeAttackLimit', 120 * 60 * 1000)
            if not sender.callMethod('GetCurrentChallengeIndex')[0] == 0:
                sender.callMethod('SetNextChallengeIndex', 0)
                sender.callMethod('NextChallenge')
            else:
                sender.callMethod('RestartChallenge')
            pre_start_executed = True
        elif not isPreStart() and pre_start_executed:
            logger.info('Leaving pre start phase')
            # reloading MatchSettings
            sender.callMethod('LoadMatchSettings', 'MatchSettings/active.txt')
            # prepare challenges
            prepareChallenges(sender, server=attached_config)
            # show server
            sender.callMethod('SetHideServer', 0)
            # remove password
            sender.callMethod('SetServerPassword', '')
            sender.callMethod('SetServerPasswordForSpectator', '')
            sender.callMethod('SetRefereePassword', '')
            # start first challenge
            challenge = sender.callMethod('GetNextChallengeInfo')[0]
            time_limit = challenge_get(challenge['UId'], attached_config)['time_limit']
            sender.callMethod('SetTimeAttackLimit', time_limit)
            sender.callMethod('NextChallenge')
            pre_start_executed = False
        elif isPostEnd() and not post_end_executed:
            logger.info('Initializing post end phase')
            # hide the server
            sender.callMethod('SetHideServer', 1)
            # set a password for server
            random.seed(time.time())
            rndpassword = hashlib.md5(str(random.randrange(int(time.time()))).encode('UTF-8')).hexdigest()
            sender.callMethod('SetServerPassword', rndpassword)
            sender.callMethod('SetServerPasswordForSpectator', rndpassword)
            sender.callMethod('SetRefereePassword', rndpassword)
            # kick all players
            kickAllPlayers(sender, 'Tournament is now over!')
            # start "endless" challenge
            sender.callMethod('SetTimeAttackLimit', 120 * 60 * 1000)
            if not sender.callMethod('GetCurrentChallengeIndex')[0] == 0:
                sender.callMethod('SetNextChallengeIndex', 0)
                sender.callMethod('NextChallenge')
            else:
                sender.callMethod('RestartChallenge')
            post_end_executed = True


def graceful_exit(signum, frame):
    raise SystemExit


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    setup_logging('Dedicated - Controller', loglevel)
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)
    rabbit = RabbitMQ()
    attached_config = rabbit.request_attachement_from_orchestrator('dcontroller')
    rabbit.attach_config(attached_config)
    config = Config.get('dedicated_run')['content'][attached_config]
    sender = GbxRemote('host.docker.internal', config['rpc_port'], 'SuperAdmin', config['superadmin_pw'])
    rabbit.consume_dedicated_state_changes(controller_function, timeout=1)
