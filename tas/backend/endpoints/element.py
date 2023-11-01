import cherrypy
import cherrypy_cors
from elements import Session


@cherrypy.popargs('element_id')
class ElementEndpointBase():
    _element = None
    _restrict_read = True  # if set to True only admin Users are allowed to use reading methods
    _restrict_write = True  # if set to True only admin Users are allowed to use writing methods
    _ro_attr = list()  # List of attribute-names, that are allways read-only

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self, element_id=None):
        if cherrypy.request.method == 'OPTIONS':
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
                return
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy_cors.preflight(allowed_methods=['GET', 'PATCH', 'DELETE'])
                return

        cookie = cherrypy.request.cookie.get('TASsession')
        if cookie:
            session = Session.get(cookie.value)
        else:
            session = Session.get(None)
        if len(session.validate_base()) > 0:
            cherrypy.response.status = 401
            return {'error': 'not authorized'}

        if cherrypy.request.method == 'GET':
            if self._restrict_read and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is not None:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                return el.json()
            else:
                result = list()
                for el in self._element.all():
                    result.append(el.json())
                return result
        elif cherrypy.request.method == 'POST':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                elif len(attr) == 0:
                    cherrypy.response.status = 400
                    return {'error': 'data is needed to be submitted'}
                attr.pop('_id', None)
                for ro in self._ro_attr:
                    attr.pop(ro, None)
                el = self._element(attr)
                result = el.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
                cherrypy.response.status = 405
                return {'error': 'POST not allowed on existing objects'}
        elif cherrypy.request.method == 'PATCH':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'PATCH not allowed on indexes'}
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                attr = cherrypy.request.json
                if not isinstance(attr, dict):
                    cherrypy.response.status = 400
                    return {'error': 'Submitted data need to be of type dict'}
                attr.pop('_id', None)
                for k, v in attr.items():
                    if k not in self._ro_attr:
                        el[k] = v
                result = el.save()
                if 'errors' in result:
                    cherrypy.response.status = 400
                else:
                    cherrypy.response.status = 201
                return result
        elif cherrypy.request.method == 'DELETE':
            if self._restrict_write and not session.admin():
                cherrypy.response.status = 403
                return {'error': 'access not allowed'}
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
                cherrypy.response.status = 405
                return {'error': 'DELETE not allowed on indexes'}
            else:
                el = self._element.get(element_id)
                if el['_id'] is None:
                    cherrypy.response.status = 404
                    return {'error': f'id {element_id} not found'}
                result = el.delete()
                if 'deleted' not in result:
                    cherrypy.response.status = 400
                return result
        else:
            if element_id is None:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, POST'
            else:
                cherrypy.response.headers['Allow'] = 'OPTIONS, GET, PATCH, DELETE'
            cherrypy.response.status = 405
            return {'error': 'method not allowed'}
