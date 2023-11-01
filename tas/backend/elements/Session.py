from elements._elementBase import ElementBase, docDB
from helpers.client import get_client_ip
from datetime import datetime
import cherrypy


class Session(ElementBase):
    _attrdef = dict(
        till=ElementBase.addAttr(type=int, notnone=True),
        ip=ElementBase.addAttr(type=str, default=None, notnone=True),
        complete=ElementBase.addAttr(type=bool, default=False),
        user_id=ElementBase.addAttr(notnone=True, fk='User')
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('User', self['user_id']):
            errors['user_id'] = {'code': 10, 'desc': f"There is no User with id '{self['user_id']}'"}
        if self['till'] <= int(datetime.now().timestamp()):
            errors['till'] = {'code': 11, 'desc': 'needs to be in the future'}
            self.delete()
        if cherrypy.request:
            if not self['ip'] == get_client_ip():
                errors['ip'] = {'code': 12, 'desc': 'does not match with the IP of request'}
                self.delete()
        return errors

    def delete_others(self):
        for sd in docDB.search_many('Session', {'user_id': self['user_id'], '_id': {'$ne': self['_id']}}):
            s = Session(sd)
            s.delete()

    def admin(self):
        p = docDB.get('User', self['user_id'])
        if p is not None:
            return p.get('admin', False)
        return False
