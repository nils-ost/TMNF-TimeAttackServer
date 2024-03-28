import json
import requests
import time
import traceback
import sys
import logging
import logging.config

EXCLUDE_RECORD_ATTRS = {
    'msg',
    'message',
    'getMessage'
}


class LokiConnector():
    _url = None

    def setup(server_ip, server_port=3100, server_protcol='http'):
        LokiConnector._url = f'{server_protcol}://{server_ip}:{server_port}'
        print('Waiting for Loki to be ready...')
        while True:
            try:
                r = requests.get(f'{LokiConnector._url}/ready')
                if r.status_code == 200:
                    print('...Loki is now ready')
                    break
            except Exception:
                pass
            time.sleep(1)

    def send_log(msg, stream, attr):
        if LokiConnector._url is None:
            return
        body = dict({
            'streams': [{
                'stream': {
                    'application': stream,
                    'level': attr.get('levelname', 'ERROR')
                },
                'values': [
                    [str(int(time.time() * 1e+9)), msg]
                ]
            }]
        })
        for k, v in attr.items():
            if isinstance(v, (bool, int, float)):
                body['streams'][0]['stream'][k] = v
            else:
                body['streams'][0]['stream'][k] = str(v)
        requests.post(f'{LokiConnector._url}/loki/api/v1/push', headers={'Content-Type': 'application/json'}, data=json.dumps(body))


class LokiHandler(logging.Handler):
    def __init__(self, stream=None):
        logging.Handler.__init__(self)
        if stream is None:
            stream = 'some-python-app'
        self.stream = stream

    def emit(self, record):
        try:
            LokiConnector.send_log(self.format(record), self.stream, self._get_attr_dict(record))
        except Exception:
            self.handleError(record)

    def _get_attr_dict(self, record):
        return {k: getattr(record, k) for k in dir(record) if not k.startswith('_') and k not in EXCLUDE_RECORD_ATTRS}


def setup_logging(stream, level=None):
    from elements import Config
    config = Config.get('loki')['content']
    loki_server = config.get('host')
    loki_port = config.get('port', 3100)
    loki_protocol = config.get('protocol', 'http')
    loki_enable = config.get('enable', True)
    loki_prefix = config.get('stream_prefix', '')
    if loki_enable and loki_server is not None:
        LokiConnector.setup(loki_server, loki_port, loki_protocol)

    logging_config = Config.get('logging')['content']
    logging_config['handlers']['loki']['stream'] = loki_prefix + stream
    if level is not None:
        for k in logging_config['handlers'].keys():
            logging_config['handlers'][k]['level'] = level
    logging.config.dictConfig(logging_config)
    logging.getLogger('pika').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    logger = logging.getLogger()

    def exc_handler(exctype, value, tb):
        logger.exception(''.join(traceback.format_exception(exctype, value, tb)))
        sys.__excepthook__(type, value, tb)  # calls default excepthook

    sys.excepthook = exc_handler
