from elements._elementBase import ElementBase, docDB
from elements import Session


class User(ElementBase):
    _attrdef = dict(
        admin=ElementBase.addAttr(type=bool, default=False, notnone=True),
        name=ElementBase.addAttr(default='', notnone=True),
        login=ElementBase.addAttr(type=str, unique=True, default=None),
        pw=ElementBase.addAttr(type=str, default=None)
    )

    @classmethod
    def get_by_login(cls, login):
        result = cls()
        fromdb = docDB.search_one(cls.__name__, {'login': login})
        if fromdb is not None:
            result._attr = fromdb
            return result
        return None

    def delete_post(self):
        for s in [Session(s) for s in docDB.search_many('Session', {'user_id': self['_id']})]:
            s.delete()
