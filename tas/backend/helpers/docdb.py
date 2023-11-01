from bson.objectid import ObjectId
from helpers.mongodb import mongoDB


class DocDB(object):
    def conn(self):
        return mongoDB()

    def coll(self, which):
        return self.conn().get_collection(which)

    def clear(self, table=None):
        if table is None:
            for c in self.conn().list_collections():
                self.conn().get_collection(c['name']).drop()
        else:
            self.conn().get_collection(table).drop()

    def exists(self, where, what_id):
        return self.get(where, what_id) is not None

    def get(self, where, what_id):
        return self.coll(where).find_one({'_id': what_id})

    def search_one(self, where, what):
        return self.coll(where).find_one(what)

    def search_many(self, where, what):
        return self.coll(where).find(what)

    def create(self, where, what_data):
        if what_data.get('_id', None) is not None:
            return False
        what_data['_id'] = str(ObjectId())
        self.coll(where).insert_one(what_data)
        return True

    def update(self, where, what_id, with_data):
        if not self.exists(where, what_id):
            return False
        self.coll(where).update_one({'_id': what_id}, with_data)
        return True

    def update_many(self, where, what_data, with_data):
        self.coll(where).update_many(what_data, with_data)
        return True

    def replace(self, where, what_data):
        if what_data.get('_id', None) is None:
            return False
        self.coll(where).replace_one({'_id': what_data['_id']}, what_data, True)
        return True

    def delete(self, where, what_id):
        self.coll(where).delete_one({'_id': what_id})

    def sum(self, where, what_field, what_filter=None):
        pipeline = list()
        if what_filter is not None:
            pipeline.append({'$match': what_filter})
        pipeline.append({'$group': {'_id': 'sum', what_field: {'$sum': f'${what_field}'}}})
        result = self.coll(where).aggregate(pipeline)
        if result.alive:
            return result.next()[what_field]
        else:
            return 0

    def count(self, where, what={}):
        return self.coll(where).count_documents(what)


docDB = DocDB()
