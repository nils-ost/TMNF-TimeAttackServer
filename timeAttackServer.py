import cherrypy
import time
from helpers.mongodb import start_mongodb_connection, challenge_all, challenge_get
from helpers.tmnf import start_processes as start_tmnf_connection, current_challenge_id, next_challenge_id
from helpers.config import get_config


class TimeAttackServer():

    @cherrypy.expose()
    def index(self):
        return "<html><body><center>Hallo</center></body></html>"

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def challenges(self):
        result = list()
        for c in challenge_all():
            result.append({'id': c['_id'], 'name': c['name']})
        return result

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def challenge_current(self):
        return challenge_get(current_challenge_id())

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def challenge_next(self):
        return challenge_get(next_challenge_id())


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    config = get_config('server')
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': config['port']})

    start_mongodb_connection()
    start_tmnf_connection()
    cherrypy.quickstart(TimeAttackServer(), '/', conf)
