import cherrypy
import cherrypy_cors
import hashlib
from datetime import datetime
from elements import Session, User
from helpers.client import get_client_ip


class LoginEndpoint():
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, user=None):
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, PUT'
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST', 'PUT'])
            return
        elif cherrypy.request.method == 'GET':
            if user is not None:
                p = User.get_by_login(user)
                if p is not None:
                    s = Session({'user_id': p['_id'], 'complete': False, 'ip': get_client_ip()})
                    s['till'] = int(datetime.now().timestamp() + 300)
                    cookie = cherrypy.response.cookie
                    cookie['TASsession'] = s.save().get('created')
                    cookie['TASsession']['path'] = '/'
                    cookie['TASsession']['max-age'] = 300
                    cookie['TASsession']['version'] = 1
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
                else:
                    cherrypy.response.status = 400
                    return {'error': 'invalid user'}
            else:
                c = cherrypy.request.cookie.get('TASsession')
                if c:
                    s = Session.get(c.value)
                else:
                    s = Session.get(None)
                if len(s.validate_base()) == 0:
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
                else:
                    cherrypy.response.status = 400
                    return {'error': 'invalid session'}
        elif cherrypy.request.method == 'POST':
            attr = cherrypy.request.json
            if not isinstance(attr, dict):
                cherrypy.response.status = 400
                return {'error': 'Submitted data need to be of type dict'}
            elif len(attr) == 0:
                cherrypy.response.status = 400
                return {'error': 'data is needed to be submitted'}
            elif 'pw' not in attr:
                cherrypy.response.status = 400
                return {'error': 'pw is missing in data'}
            c = cherrypy.request.cookie.get('TASsession')
            if c:
                s = Session.get(c.value)
            else:
                s = Session.get(None)
            if not len(s.validate_base()) == 0:
                cherrypy.response.status = 400
                return {'error': 'invalid session'}
            else:
                p = User.get(s['user_id'])
                m = hashlib.md5()
                m.update(s['_id'].encode('utf-8'))
                m.update(p['pw'].encode('utf-8'))
                if not m.hexdigest().lower() == attr['pw'].lower():
                    s.delete()
                    cherrypy.response.status = 400
                    return {'error': 'invalid password'}
                else:
                    s['complete'] = True
                    s['till'] = int(datetime.now().timestamp() + 60 * 60 * 24)
                    s.save()
                    s.delete_others()
                    cookie = cherrypy.response.cookie
                    cookie['TASsession'] = s['_id']
                    cookie['TASsession']['path'] = '/'
                    cookie['TASsession']['max-age'] = 60 * 60 * 24
                    cookie['TASsession']['version'] = 1
                    cherrypy.response.status = 201
                    return {'session_id': s['_id'], 'till': s['till'], 'complete': s['complete']}
        elif cherrypy.request.method == 'PUT':
            c = cherrypy.request.cookie.get('TASsession')
            if c:
                s = Session.get(c.value)
                s.delete()
            cherrypy.response.status = 201
            return {'logout': 'done'}
        else:
            cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST, PUT'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
