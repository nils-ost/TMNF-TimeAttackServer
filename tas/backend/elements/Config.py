from elements._elementBase import ElementBase, docDB


class Config(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(type=str, unique=True, notnone=True),
        content=ElementBase.addAttr(type=dict, default={}, notnone=True)
    )

    _defaults = {
        'dedicated': {
            'TMNF-TAS': {
                'connection': 'local-container',
                'container': 'tmnfd-static',
                'type': 'tmnf'
            }
        },
        'challenges': {
            'rel_time': 'SilverTime',
            'least_rounds': 6,
            'least_time': 300000
        },
        's3': {
            'host': 'minio',
            'port': 9000,
            'access_key': 'tmtas',
            'access_secret': 'password',
            'bucket_replays': 'tas-replays',
            'bucket_thumbnails': 'tas-thumbnails',
            'bucket_challenges': 'tas-challenges'
        },
        'rabbit': {
            'host': 'rabbitmq',
            'port': 5672,
            'queue_dedicated_received_messages': 'tas_ded_rx_msg',
            'queue_dedicated_state_changes': 'tas_ded_st_chg',
            'queue_orchestrator': 'tas_orchestrator'
        }
    }

    @classmethod
    def get(cls, name):
        result = cls()
        fromdb = docDB.search_one(cls.__name__, {'name': name})
        if fromdb is not None:
            result._attr = fromdb
        elif name in cls._defaults:
            result['name'] = name
            result['content'] = cls._defaults[name]
            result.save()
        else:
            result['name'] = name
        return result
