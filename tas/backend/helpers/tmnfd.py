"""
TrachMania Nations Forever - Dedicated Server
"""
from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_get, challenge_add, challenge_update, challenge_deactivate_all, challenge_id_get, challenge_id_set
from helpers.mongodb import player_update, player_get, ranking_clear, ranking_rebuild, set_tmnfd_name, bestlaptime_get, clean_player_id
from helpers.mongodb import get_provide_replays, get_provide_thumbnails, get_provide_challenges, replay_add, get_start_time, get_end_time
from helpers.tmnfdcli import tmnfd_cli_test, tmnfd_cli_upload_replay, tmnfd_cli_generate_thumbnails, tmnfd_cli_upload_challenges
import time
import sys
import hashlib
import random

config = get_config('tmnf-server')
challenge_config = get_config('challenges')

watcher_process = None


def isPreStart():
    startts = get_start_time()
    if startts is None:
        return False
    if time.time() < startts:
        return True
    return False


def isPostEnd():
    endts = get_end_time()
    if endts is None:
        return False
    if time.time() > endts:
        return True
    return False


def calcTimeLimit(rel_time, lap_race, nb_laps):
    if lap_race and nb_laps < 1:
        new_time = challenge_config['least_time']
    elif lap_race and nb_laps > 1:
        new_time = (rel_time / nb_laps) * challenge_config['least_rounds']
    else:
        new_time = rel_time * challenge_config['least_rounds']
    return int(max(new_time, challenge_config['least_time']))


def prepareChallenges(sender):
    challenge_deactivate_all()
    starting_index = 0
    infos_returned = 10
    fetched_count = 0
    while True:
        for challenge in sender.callMethod('GetChallengeList', infos_returned, starting_index)[0]:
            challenge = sender.callMethod('GetChallengeInfo', challenge['FileName'])[0]
            rel_time = challenge.get(challenge_config['rel_time'], 30000)
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
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    time_limit = challenge_get(challenge['UId'])['time_limit']
    sender.callMethod('SetTimeAttackLimit', time_limit)
    challenge_id_set(challenge['UId'], next=True)
    print(f"Challenge next: {challenge['Name']} - AttackLimit: {int(time_limit / 1000)}s")


def sendLaptimeNotice(sender, player_login, player_time=None):
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
        msg = "You don't have a PB on this Challenge yet"
    elif player_time is None:
        msg = f"Your PB on this Challenge is: {timetos(best['time'])}"
    elif player_time == 0:
        pass
    elif player_time == best['time']:
        msg = f"You drove a PB with: {timetos(best['time'])}"
    elif best['time'] is not None:
        msg = f"You drove {timetos(player_time)} thats {timetos(player_time - best['time'])} behind your PB ({timetos(best['time'])})"
    if msg:
        sender.callMethod('SendNoticeToId', player['current_uid'], msg, 255, 20)


def kickAllPlayers(sender, msg):
    for p in sender.callMethod('GetPlayerList', 0, 0)[0]:
        sender.callMethod('Kick', p['Login'], msg)


def worker_function(msg_queue, sender):
    while True:
        func, params = msg_queue.get()

        if func == 'TrackMania.PlayerFinish':
            current_challenge = challenge_id_get(current=True)
            if current_challenge is not None:
                player_id, player_login, player_time = params
                ts, new_best = laptime_add(player_login, current_challenge, player_time)
                if player_time > 0:
                    print(f'{player_login} drove: {player_time / 1000}')
                sendLaptimeNotice(sender, player_login, player_time)
                if new_best and get_provide_replays():
                    player_hash = hashlib.md5(player_login.encode('utf-8')).hexdigest()
                    replay_name = f'{player_hash}_{ts}'
                    if sender.callMethod('SaveBestGhostsReplay', player_login, replay_name)[0]:
                        if tmnfd_cli_upload_replay(replay_name):
                            replay_add(player_login, current_challenge, ts, replay_name)
                            print(f'Providing Replay: {replay_name}')
                        else:
                            print('Replay could not be provided!')
                    else:
                        print('Replay could not be provided!')

        elif func == 'TrackMania.BeginRace':
            if isPreStart() or isPostEnd():
                if isPostEnd():
                    challenge_id_set(params[0]['UId'], current=True)
                    next_challenge = sender.callMethod('GetNextChallengeInfo')[0]
                    challenge_id_set(next_challenge['UId'], next=True)
                    print(f"Post End Challenge begin: {params[0]['Name']}")
                else:
                    challenge_id_set(None, current=True)
                    challenge_id_set(None, next=True)
                    print(f"Pre Start Challenge begin: {params[0]['Name']}")
            else:
                challenge_db = challenge_get(params[0]['UId'])
                if challenge_db['lap_race'] and challenge_db['nb_laps'] == -1:
                    new_time = calcTimeLimit(challenge_db['rel_time'], True, params[0]['NbLaps'])
                    challenge_update(params[0]['UId'], time_limit=new_time, nb_laps=params[0]['NbLaps'])
                else:
                    challenge_update(params[0]['UId'])
                challenge_id_set(params[0]['UId'], current=True)
                print(f"Challenge begin: {params[0]['Name']}")
                prepareNextChallenge(sender)
                for p in sender.callMethod('GetPlayerList', 0, 0)[0]:
                    sendLaptimeNotice(sender, p['Login'])

        elif func == 'TrackMania.EndRace':
            if not isPreStart() and not isPostEnd():
                old_challenge = challenge_id_get(current=True)
                challenge_id_set(None, current=True)
                if old_challenge is not None:
                    ranking_rebuild(old_challenge)
                print(f"Challenge end: {params[1]['Name']}")

        elif func == 'TrackMania.PlayerInfoChanged':
            player = params[0]
            player_update(player['Login'], player['NickName'], player['PlayerId'])
            player_db = player_get(clean_player_id(player['Login']))
            if player_db is not None and not player_db['connect_msg_send']:
                sendLaptimeNotice(sender, player['Login'])
                player_update(player['Login'], connect_msg_send=True)

        elif func == 'TrackMania.PlayerConnect':
            print(f'{params[0]} connected')
            player_update(params[0], connected=True, connect_msg_send=False)

        elif func == 'TrackMania.PlayerDisconnect':
            print(f'{params[0]} disconnected')
            player_update(params[0], connected=False)


def receiver_function(msg_queue, receiver):
    while True:
        try:
            msg_queue.put(receiver.receiveCallback())
        except ConnectionResetError:
            print('Lost connection to: TMNF - Dedicated Server')
            challenge_id_set(None, current=True)
            challenge_id_set(None, next=True)
            return


def watcher_function():
    BaseManager.register('GbxRemote', GbxRemote)
    manager = BaseManager()
    manager.start()
    receiver = manager.GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender = manager.GbxRemote(config['host'], config['port'], config['user'], config['password'])

    callback_queue = Queue()
    worker_process = Process(target=worker_function, args=(callback_queue, sender, ), daemon=True)
    worker_process.start()
    receiver_process = Process(target=receiver_function, args=(callback_queue, receiver, ), daemon=True)

    first_start = True
    pre_start_executed = False
    post_end_executed = False
    while True:
        if not receiver_process.is_alive():
            delay_counter = 0
            while not receiver.connect():
                if delay_counter == 0:
                    print('Waiting for: TMNF - Dedicated Server')
                delay_counter = (delay_counter + 1) % 30
                time.sleep(1)
            while not sender.connect():
                time.sleep(1)
            print('Connected to: TMNF - Dedicated Server')
            prepareChallenges(sender)

            if get_provide_replays() or get_provide_thumbnails() or get_provide_challenges():
                tmnfd_cli_test()
                if get_provide_thumbnails() and tmnfd_cli_generate_thumbnails():
                    print('Generated Thumbnails')
                if get_provide_challenges() and tmnfd_cli_upload_challenges():
                    print('Uploaded Challenges')

            server_name = sender.callMethod('GetServerName')[0]
            set_tmnfd_name(server_name)
            print(f'TMNF - Dedicated Server Name: {server_name}')
            if not isPreStart() and not isPostEnd():
                current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
                challenge_update(current_challenge['UId'], force_inc=False)
                print(f"Challenge current: {current_challenge['Name']}")
                challenge_id_set(current_challenge['UId'], current=True)
                prepareNextChallenge(sender)
            if first_start:
                first_start = False
            else:
                if sys.version_info.minor >= 7:
                    receiver_process.close()
                receiver_process = Process(target=receiver_function, args=(callback_queue, receiver, ), daemon=True)
            receiver_process.start()
        if isPreStart() and not pre_start_executed:
            print('Initializing pre start phase')
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
            print('Leaving pre start phase')
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
            print('Initializing post end phase')
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
        time.sleep(1)


def connect():
    global watcher_process

    if watcher_process is None:
        watcher_process = Process(target=watcher_function)
        watcher_process.start()
