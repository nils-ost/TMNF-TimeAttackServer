from multiprocessing import Process, Queue
from helpers.config import get_config
from helpers.GbxRemote import GbxRemote
from helpers.mongodb import laptime_add, challenge_add, player_update

config = get_config('tmnf-server')
challenge_config = get_config('challenges')

receiver = None
sender = None

callback_queue = Queue()
receiver_process = None
worker_process = None

current_challenge = None
next_challenge = None


def setNextChallengeTimeLimit():
    global next_challenge
    challenge = sender.callMethod('GetNextChallengeInfo')[0]
    new_time = 0
    if challenge['LapRace']:
        new_time = (challenge['SilverTime'] / challenge['NbLaps']) * challenge_config['least_rounds']
    else:
        new_time = challenge['SilverTime'] * challenge_config['least_rounds']
    new_time = max(new_time, challenge_config['least_time'])
    sender.callMethod('SetTimeAttackLimit', new_time)
    next_challenge = challenge['UId']
    print(f"Challenge next: {challenge['Name']} - AttackLimit: {int(new_time / 1000)}s")


def receiver_function(msg_queue):
    global current_challenge
    while True:
        func, params = msg_queue.get()

        if func == 'TrackMania.PlayerFinish':
            if current_challenge is not None:
                player_id, player_login, player_time = params
                laptime_add(player_login, current_challenge, player_time)
                if player_time > 0:
                    print(f"{player_login} drove: {player_time / 1000}")

        elif func == 'TrackMania.BeginRace':
            challenge_add(params[0]['UId'], params[0]['Name'])
            current_challenge = params[0]['UId']
            print(f"Challenge begin: {params[0]['Name']}")
            setNextChallengeTimeLimit()

        elif func == 'TrackMania.EndRace':
            current_challenge = None
            print(f"Challenge end: {params[1]['Name']}")

        elif func == 'TrackMania.PlayerInfoChanged':
            player = params[0]
            player_update(player['Login'], player['NickName'], player['PlayerId'])

        elif func == 'TrackMania.PlayerConnect':
            print(f"{params[0]} connected")

        elif func == 'TrackMania.PlayerDisconnect':
            print(f"{params[0]} disconnected")


def worker_function(msg_queue):
    global receiver
    while True:
        msg_queue.put(receiver.receiveCallback())


def start_processes():
    global worker_process
    global receiver_process
    global receiver
    global sender
    global config
    global current_challenge

    receiver = GbxRemote(config['host'], config['port'], config['user'], config['password'])
    sender = GbxRemote(config['host'], config['port'], config['user'], config['password'])

    current_challenge = sender.callMethod('GetCurrentChallengeInfo')[0]
    challenge_add(current_challenge['UId'], current_challenge['Name'])
    print(f"Challenge current: {current_challenge['Name']}")
    current_challenge = current_challenge['UId']
    setNextChallengeTimeLimit()

    if worker_process is None:
        worker_process = Process(target=worker_function, args=(callback_queue, ), daemon=True)
        worker_process.start()
    if receiver_process is None:
        receiver_process = Process(target=receiver_function, args=(callback_queue, ), daemon=True)
        receiver_process.start()


def current_challenge_id():
    return current_challenge


def next_challenge_id():
    return next_challenge
