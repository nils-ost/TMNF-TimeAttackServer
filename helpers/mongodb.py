from pymongo import MongoClient, ASCENDING, DESCENDING
from helpers.config import get_config
from datetime import datetime

mongoClient = None
_mongoDB = None
config = get_config('mongo')


def start_mongodb_connection():
    global mongoClient
    global _mongoDB
    if mongoClient is None:
        mongoClient = MongoClient(host=config['host'], port=int(config['port']), serverSelectionTimeoutMS=500)
        _mongoDB = mongoClient.get_database(config['database'])


def mongoDB():
    global _mongoDB
    if _mongoDB is None:  # pragma: no cover
        start_mongodb_connection()
    return _mongoDB


def is_connected():
    global mongoClient
    try:
        mongoClient.admin.command('ismaster')
        return True
    except Exception:  # pragma: no cover
        return False


"""
TMNF-TimeAttack
"""


def laptime_add(player_id, challange_id, time):
    if time > 0:
        ts = int(datetime.now().timestamp())
        lt = {'player_id': player_id, 'challange_id': challange_id, 'time': time, 'created_at': ts}
        mongoDB().laptimes.insert_one(lt)
        best = mongoDB().bestlaptimes.find_one({'player_id': player_id, 'challange_id': challange_id})
        if best is None:
            mongoDB().bestlaptimes.insert_one(lt)
        elif best['time'] > time:
            mongoDB().bestlaptimes.update_one({'_id': best['_id']}, {'$set': {'time': time, 'created_at': ts}})


"""
brick
"""


def brick_get(brick_id):
    """
    Returns a brick from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    brick = _mongoDB.bricks.find_one({'_id': brick_id})
    if brick is None:
        brick = {}
        feature_update(brick, 'all', -1, 0)
        brick['_id'] = brick_id
    return brick


def brick_save(brick):
    """
    Saves brick to DB
    """
    global _mongoDB
    _mongoDB.bricks.replace_one({'_id': brick['_id']}, brick, True)


def brick_delete(brick_id):
    """
    Removes brick from DB
    """
    global _mongoDB
    _mongoDB.bricks.delete_one({'_id': brick_id})


def brick_exists(brick_id):
    """
    Returns True or False whether a brick is stored in DB or not
    """
    global _mongoDB
    brick = _mongoDB.bricks.find_one({'_id': brick_id})
    if brick is not None:
        return True
    return False


def brick_all():  # pragma: no cover
    """
    Returns an iterator to all bricks in DB
    """
    global _mongoDB
    return _mongoDB.bricks.find({})


def brick_all_ids():
    """
    Returns a list of all brick's id's present in DB
    """
    global _mongoDB
    ids = []
    for brick in _mongoDB.bricks.find({}):
        ids.append(brick['_id'])
    return ids


def brick_count():
    """
    Returns number of bricks present in DB
    """
    global _mongoDB
    return _mongoDB.bricks.count_documents({})


"""
temp
"""


def temp_sensor_get(sensor_id):
    """
    Returns a temp_sensor from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    sensor = _mongoDB.temp_sensors.find_one({'_id': sensor_id})
    if sensor is None:
        sensor = {}
        sensor.update(copy.deepcopy(temp_sensor_defaults))
        sensor['_id'] = sensor_id
    return sensor


def temp_sensor_save(sensor):
    """
    Saves temp_sensor to DB
    """
    global _mongoDB
    _mongoDB.temp_sensors.replace_one({'_id': sensor['_id']}, sensor, True)


def temp_sensor_delete(sensor_id):
    """
    Removes temp_sensor from DB
    """
    global _mongoDB
    _mongoDB.temp_sensors.delete_one({'_id': sensor_id})


def temp_sensor_exists(sensor_id):
    """
    Returns True or False whether a temp_sensor is stored in DB or not
    """
    global _mongoDB
    sensor = _mongoDB.temp_sensors.find_one({'_id': sensor_id})
    if sensor is not None:
        return True
    return False


def temp_sensor_all():  # pragma: no cover
    """
    Returns an iterator to all temp_sensors in DB
    """
    global _mongoDB
    return _mongoDB.temp_sensors.find({})


def temp_sensor_count():
    """
    Returns number of tempsensors present in DB
    """
    global _mongoDB
    return _mongoDB.temp_sensors.count_documents({})


"""
humid
"""


def humid_get(sensor_id):
    """
    Returns a humidity sensor from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    sensor = _mongoDB.humid_sensors.find_one({'_id': sensor_id})
    if sensor is None:
        sensor = {}
        sensor.update(copy.deepcopy(humid_defaults))
        sensor['_id'] = sensor_id
    return sensor


def humid_save(sensor):
    """
    Saves humidity sensor to DB
    """
    global _mongoDB
    _mongoDB.humid_sensors.replace_one({'_id': sensor['_id']}, sensor, True)


def humid_delete(sensor_id):
    """
    Removes humidity sensor from DB
    """
    global _mongoDB
    _mongoDB.humid_sensors.delete_one({'_id': sensor_id})


def humid_exists(sensor_id):
    """
    Returns True or False whether a humidity sensor is stored in DB or not
    """
    global _mongoDB
    sensor = _mongoDB.humid_sensors.find_one({'_id': sensor_id})
    if sensor is not None:
        return True
    return False


def humid_all():  # pragma: no cover
    """
    Returns an iterator to all humidity sensors in DB
    """
    global _mongoDB
    return _mongoDB.humid_sensors.find({})


def humid_count():
    """
    Returns number of humidity sensors present in DB
    """
    global _mongoDB
    return _mongoDB.humid_sensors.count_documents({})


"""
latch
"""


def latch_get(brick_id, latch_id):
    """
    Returns a latch from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    lid = brick_id + '_' + str(latch_id)
    latch = _mongoDB.latches.find_one({'_id': lid})
    if latch is None:
        latch = dict()
        latch.update(copy.deepcopy(latch_defaults))
        latch['_id'] = lid
    return latch


def latch_save(latch):
    """
    Saves latch to DB
    """
    global _mongoDB
    _mongoDB.latches.replace_one({'_id': latch['_id']}, latch, True)


def latch_delete(brick_id, latch_id):
    """
    Removes latch from DB
    """
    global _mongoDB
    lid = brick_id + '_' + str(latch_id)
    _mongoDB.latches.delete_one({'_id': lid})


def latch_exists(brick_id, latch_id):
    """
    Returns True or False whether a latch is stored in DB or not
    """
    global _mongoDB
    lid = brick_id + '_' + str(latch_id)
    latch = _mongoDB.latches.find_one({'_id': lid})
    if latch is not None:
        return True
    return False


def latch_all():  # pragma: no cover
    """
    Returns an iterator to all latches in DB
    """
    global _mongoDB
    return _mongoDB.latches.find({})


def latch_count():
    """
    Returns number of latches present in DB
    """
    global _mongoDB
    return _mongoDB.latches.count_documents({})


"""
signal
"""


def signal_get(brick_id, signal_id):
    """
    Returns a signal from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    sid = brick_id + '_' + str(signal_id)
    signal = _mongoDB.signals.find_one({'_id': sid})
    if signal is None:
        signal = dict()
        signal.update(copy.deepcopy(signal_defaults))
        signal['_id'] = sid
    return signal


def signal_save(signal):
    """
    Saves signal to DB
    """
    global _mongoDB
    _mongoDB.signals.replace_one({'_id': signal['_id']}, signal, True)


def signal_delete(signal):
    """
    Removes signal from DB
    """
    global _mongoDB
    _mongoDB.signals.delete_one({'_id': signal['_id']})


def signal_exists(brick_id, signal_id):
    """
    Returns True or False whether a signal is stored in DB or not
    """
    global _mongoDB
    sid = brick_id + '_' + str(signal_id)
    signal = _mongoDB.signals.find_one({'_id': sid})
    if signal is not None:
        return True
    return False


def signal_all(brick_id=None):  # pragma: no cover
    """
    Returns an iterator to all signals in DB if brick_id is None
    Otherwise returns an iterator to all signals of a specific brick
    """
    global _mongoDB
    if brick_id is None:
        return _mongoDB.signals.find({}).sort("_id", ASCENDING)
    else:
        return _mongoDB.signals.find({'_id': {'$regex': '^' + str(brick_id) + '_'}}).sort("_id", ASCENDING)


def signal_count():
    """
    Returns number of signals present in DB
    """
    global _mongoDB
    return _mongoDB.signals.count_documents({})


"""
fwmetadata
"""


def fwmetadata_get(brick_type, version):
    """
    Returns FirmwareMetadata from DB or None if it doesn't exist in DB
    """
    global _mongoDB
    mid = f"{brick_type}_{version}"
    return _mongoDB.fwmetadata.find_one({'_id': mid})


def fwmetadata_save(metadata):
    """
    Saves FirmwareMetadata to DB
    """
    global _mongoDB
    if '_id' not in metadata:
        metadata['_id'] = f"{metadata['brick_type']}_{metadata['version']}"
    if 'dev' not in metadata:
        metadata['dev'] = False
    _mongoDB.fwmetadata.replace_one({'_id': metadata['_id']}, metadata, True)


def fwmetadata_delete(metadata):
    """
    Removes FirmwareMetadata from DB
    """
    global _mongoDB
    if '_id' not in metadata:  # pragma: no cover
        metadata['_id'] = f"{metadata['brick_type']}_{metadata['version']}"
    _mongoDB.fwmetadata.delete_one({'_id': metadata['_id']})


def fwmetadata_exists(brick_type, version):
    """
    Returns True or False whether FirmwareMetadata is stored in DB or not
    """
    global _mongoDB
    mid = f"{brick_type}_{version}"
    fm = _mongoDB.fwmetadata.find_one({'_id': mid})
    if fm is not None:
        return True
    return False


def fwmetadata_all(brick_type=None):
    """
    Returns an iterator to all FirmwareMetadata in DB if brick_type is None
    Otherwise returns an iterator to all FirmwareMetadata of a specific brick_type
    """
    global _mongoDB
    if brick_type is None:
        return _mongoDB.fwmetadata.find({}).sort("_id", ASCENDING)
    else:
        return _mongoDB.fwmetadata.find({'brick_type': brick_type}).sort("_id", ASCENDING)


def fwmetadata_search(brick_type, sketchMD5):
    """
    Returns FirmwareMetadata with a specific brick_type and sketchMD5 or None if it not exits
    """
    global _mongoDB
    return _mongoDB.fwmetadata.find_one({'brick_type': brick_type, 'sketchMD5': sketchMD5})


def fwmetadata_latest(brick_type):
    """
    Returns FirmwareMetadata with newest version for given brick_type
    """
    global _mongoDB
    return _mongoDB.fwmetadata.find_one({'brick_type': brick_type}, sort=[('_id', DESCENDING)], limit=1)


def fwmetadata_count():
    """
    Returns number of FirmwareMetadata present in DB
    """
    global _mongoDB
    return _mongoDB.fwmetadata.count_documents({})


"""
util
"""


def util_get(util_id):
    """
    Returns a util from DB or a newly created it if doesn't exist in DB
    """
    global _mongoDB
    util = _mongoDB.util.find_one({'_id': util_id})
    if util is None:
        util = {'_id': util_id}
    return util


def util_save(util):
    """
    Saves util to DB
    """
    global _mongoDB
    _mongoDB.util.replace_one({'_id': util['_id']}, util, True)
