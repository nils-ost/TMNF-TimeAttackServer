"""
TrachMania Nations Forever - Dedicated Server Watcher
"""
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import challenge_get, challenge_update, challenge_deactivate_all, challenge_id_set
from helpers.mongodb import set_tmnfd_name, get_provide_replays, get_provide_thumbnails, get_provide_challenges
from helpers.tmnfd import isPreStart, isPostEnd, prepareChallenges, prepareNextChallenge, kickAllPlayers
from helpers.tmnfdcli import tmnfd_cli_test, tmnfd_cli_generate_thumbnails, tmnfd_cli_upload_challenges
from helpers.rabbitmq import consume_dedicated_state_changes
import time
import hashlib
import random
import logging

logger = logging.getLogger(__name__)
config = get_config('tmnf-server')
sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])
pre_start_executed = False
post_end_executed = False
dedicated_connected = False


def watcher_function(timeout, new_state, ch, delivery_tag):
    global sender
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
            prepareChallenges(sender)

            if get_provide_replays() or get_provide_thumbnails() or get_provide_challenges():
                tmnfd_cli_test()
                if get_provide_thumbnails() and tmnfd_cli_generate_thumbnails():
                    logger.info('Generated Thumbnails')
                if get_provide_challenges() and tmnfd_cli_upload_challenges():
                    logger.info('Uploaded Challenges')

            server_name = sender.callMethod('GetServerName')[0]
            set_tmnfd_name(server_name)
            logger.info(f'TMNF - Dedicated Server Name: {server_name}')
            if not isPreStart() and not isPostEnd():
                current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
                challenge_update(current_challenge['UId'], force_inc=False)
                logger.info(f"Challenge current: {current_challenge['Name']}")
                challenge_id_set(current_challenge['UId'], current=True)
                prepareNextChallenge(sender)
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
            # deaktivate all challenges
            challenge_deactivate_all()
            # clear current and next challenge
            challenge_id_set(None, current=True)
            challenge_id_set(None, next=True)
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
            prepareChallenges(sender)
            # show server
            sender.callMethod('SetHideServer', 0)
            # remove password
            sender.callMethod('SetServerPassword', '')
            sender.callMethod('SetServerPasswordForSpectator', '')
            sender.callMethod('SetRefereePassword', '')
            # start first challenge
            challenge = sender.callMethod('GetNextChallengeInfo')[0]
            time_limit = challenge_get(challenge['UId'])['time_limit']
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


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', level='INFO')
    consume_dedicated_state_changes(watcher_function, timeout=1)
