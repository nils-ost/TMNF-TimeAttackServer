"""
TrachMania Nations Forever - Dedicated Server - Helpers
"""
from elements import Config
from helpers.mongodb import challenge_get, challenge_add, challenge_deactivate_all, challenge_id_get, challenge_id_set
from helpers.mongodb import player_get, ranking_clear, ranking_rebuild, bestlaptime_get, clean_player_id
from helpers.mongodb import get_start_time, get_end_time
from helpers.mongodb import get_hotseat_mode, hotseat_player_ingameid_get
import time
import logging
import sys

logger = logging.getLogger(__name__)
challenge_config = Config.get('challenges')['content']


def isPreStart():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    startts = get_start_time()
    if startts is None:
        return False
    if time.time() < startts:
        return True
    return False


def isPostEnd():
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    endts = get_end_time()
    if endts is None:
        return False
    if time.time() > endts:
        return True
    return False


def calcTimeLimit(rel_time, lap_race, nb_laps):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    if lap_race and nb_laps < 1:
        new_time = challenge_config['least_time']
    elif lap_race and nb_laps > 1:
        new_time = (rel_time / nb_laps) * challenge_config['least_rounds']
    else:
        new_time = rel_time * challenge_config['least_rounds']
    return int(max(new_time, challenge_config['least_time']))


def prepareChallenges(sender):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    challenge_deactivate_all()
    starting_index = 0
    infos_returned = 10
    fetched_count = 0
    while True:
        for challenge in sender.callMethod('GetChallengeList', infos_returned, starting_index)[0]:
            challenge = sender.callMethod('GetChallengeInfo', challenge['FileName'])[0]
            rel_time = challenge.get(challenge_config['rel_time'], 30000)
            if get_hotseat_mode():
                time_limit = 60 * 60 * 1000
            else:
                time_limit = calcTimeLimit(rel_time, challenge['LapRace'], challenge['NbLaps'])
            challenge_add(challenge['UId'], challenge['Name'], time_limit, rel_time, challenge['LapRace'])
            fetched_count += 1
        if fetched_count % infos_returned == 0:
            starting_index += infos_returned
        else:
            break
    ranking_clear()
    ranking_rebuild()


def prepareNextChallenge(sender):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    time_limit = challenge_get(challenge['UId'])['time_limit']
    sender.callMethod('SetTimeAttackLimit', time_limit)
    challenge_id_set(challenge['UId'], next=True)
    logger.info(f"Challenge next: {challenge['Name']} - AttackLimit: {int(time_limit / 1000)}s")


def sendLaptimeNotice(sender, player_login, player_time=None):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')

    def timetos(time):
        if time is None:
            return '---'
        m = int(abs(time) / 10)
        ms = int(m % 100)
        m = int(m / 100)
        s = int(m % 60)
        m = int(m / 60)
        return f"{'-' if time < 0 else ''}{m}:{'0' if s < 10 else ''}{s}.{'0' if ms < 10 else ''}{ms}"
    player_id = clean_player_id(player_login)
    player = player_get(player_id=player_id)
    if player is None:
        return
    best = bestlaptime_get(player_id=player_id, challenge_id=challenge_id_get(current=True))
    msg = None
    if best is None:
        if get_hotseat_mode():
            msg = f'Hello {player_login}. Have fun on the HotSeat!'
        else:
            msg = "You don't have a PB on this Challenge yet"
    elif player_time is None:
        if get_hotseat_mode():
            msg = f"Welcome back {player_login}! Your PB is: {timetos(best['time'])}"
        else:
            msg = f"Your PB on this Challenge is: {timetos(best['time'])}"
    elif player_time == 0:
        pass
    elif player_time == best['time']:
        msg = f"You drove a PB with: {timetos(best['time'])}"
    elif best['time'] is not None:
        msg = f"You drove {timetos(player_time)} thats {timetos(player_time - best['time'])} behind your PB ({timetos(best['time'])})"
    if msg:
        if get_hotseat_mode():
            sender.callMethod('SendNoticeToId', hotseat_player_ingameid_get(), msg, 255, 20)
        else:
            sender.callMethod('SendNoticeToId', player['current_uid'], msg, 255, 20)


def kickAllPlayers(sender, msg):
    logger.debug(f'{sys._getframe().f_code.co_name} {locals()}')
    for p in sender.callMethod('GetPlayerList', 0, 0)[0]:
        sender.callMethod('Kick', p['Login'], msg)
