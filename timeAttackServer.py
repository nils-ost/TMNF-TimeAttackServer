import cherrypy
import time
from helpers.mongodb import challenge_all, challenge_get, player_all
from helpers.tmnf import start_processes as start_tmnf_connection, current_challenge_id, next_challenge_id
from helpers.config import get_config


class TimeAttackServer():
    def __init__(self):
        self.challenges = Challenges()
        self.players = Players()

    @cherrypy.expose()
    def index(self):
        return "<html><body><center>Hallo</center></body></html>"


class Challenges():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = list()
        for c in challenge_all():
            result.append({'id': c['_id'], 'name': c['name']})
        return result

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def current(self):
        return challenge_get(current_challenge_id())

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def next(self):
        return challenge_get(next_challenge_id())


class Players():
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        result = list()
        for p in player_all():
            result.append({'id': p['_id'], 'name': p['nickname']})
        return result


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    config = get_config('server')
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port']})

    start_tmnf_connection()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
