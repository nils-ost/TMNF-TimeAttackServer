from pymongo import MongoClient, ASCENDING, DESCENDING
from helpers.config import get_config
from datetime import datetime
import multiprocessing

_mongoDB = dict()
config = get_config('mongo')


def start_mongodb_connection():
    global _mongoDB
    mongoClient = MongoClient(host=config['host'], port=int(config['port']), serverSelectionTimeoutMS=500)
    _mongoDB[multiprocessing.current_process().name] = mongoClient.get_database(config['database'])


def mongoDB():
    global _mongoDB
    p = multiprocessing.current_process().name
    if p not in _mongoDB:
        start_mongodb_connection()
    return _mongoDB[p]


"""
TMNF-TimeAttack
"""


def clean_player_id(player_id):
    return player_id.rsplit(':', 1)[0]


def print_all():
    print('challenges:')
    for c in mongoDB().challenges.find({}):
        print(c)
    print('players:')
    for p in mongoDB().players.find({}):
        print(p)
    print('laptimes:')
    for l in mongoDB().laptimes.find({}):
        print(l)
    print('bestlaptimes:')
    for l in mongoDB().bestlaptimes.find({}):
        print(l)


def laptime_add(player_id, challenge_id, time):
    ts = int(datetime.now().timestamp())
    player_id = clean_player_id(player_id)
    lt = {'player_id': player_id, 'challenge_id': challenge_id, 'time': time, 'created_at': ts}
    if time > 0:
        mongoDB().laptimes.insert_one(lt)
        best = mongoDB().bestlaptimes.find_one({'player_id': player_id, 'challenge_id': challenge_id})
        if best is None:
            mongoDB().bestlaptimes.insert_one(lt)
        elif best['time'] is None or best['time'] > time:
            mongoDB().bestlaptimes.update_one({'_id': best['_id']}, {'$set': {'time': time, 'created_at': ts}})
    elif time == 0 and mongoDB().bestlaptimes.find_one({'player_id': player_id, 'challenge_id': challenge_id}) is None:
        lt['time'] = None
        mongoDB().bestlaptimes.insert_one(lt)


def player_update(player_id, nickname, current_uid):
    ts = int(datetime.now().timestamp())
    player_id = clean_player_id(player_id)
    player = mongoDB().players.find_one({'_id': player_id})
    if player is None:
        mongoDB().players.insert_one({'_id': player_id, 'current_uid': current_uid, 'nickname': nickname, 'last_update': ts})
    else:
        mongoDB().players.update_one({'_id': player_id}, {'$set': {'nickname': nickname, 'current_uid': current_uid, 'last_update': ts}})


def player_all():
    return mongoDB().players.find({})


def challenge_add(challenge_id, name):
    challenge = mongoDB().challenges.find_one({'_id': challenge_id})
    if challenge is None:
        mongoDB().challenges.insert_one({'_id': challenge_id, 'name': name})


def challenge_all():
    return mongoDB().challenges.find({})


def challenge_get(challenge_id):
    return mongoDB().challenges.find_one({'_id': challenge_id})


def ranking_for(challenge_id):
    result = list()
    next_points = 1
    for lt in mongoDB().bestlaptimes.find({'challenge_id': challenge_id, 'time': None}):
        result.append({'player_id': lt['player_id'], 'points': 0, 'time': lt['time'], 'at': lt['created_at']})
        next_points += 1
    for lt in mongoDB().bestlaptimes.find({'challenge_id': challenge_id, 'time': {'$ne': None}}).sort('time', DESCENDING):
        result.append({'player_id': lt['player_id'], 'points': next_points, 'time': lt['time'], 'at': lt['created_at']})
        next_points += 1
    return result


def ranking_global():
    pp = dict()
    for c in [c['_id'] for c in challenge_all()]:
        for player, points in [(p['player_id'], p['points']) for p in ranking_for(c)]:
            if player not in pp:
                pp[player] = points
            else:
                pp[player] += points
    result = list()
    for player, points in pp.items():
        result.append({'player_id': player, 'points': points})
    return result
