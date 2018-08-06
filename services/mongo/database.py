import re
from datetime import time

from bson import ObjectId
from pymongo import MongoClient

from dance.service import IService

def json_to_bson(obj):
    for name in obj:
        value = obj[name]
        if type(value) == str:
            if re.match(r'^[0-9 a-f]{24}$', value) is not None:
                obj[name] = ObjectId(value)
            elif re.match(r'^D:([0-9]*)$', value) is not None:
                obj[name] = time.time()
            else:
                pass
        elif isinstance(value, list):
            for index in range(len(value)):
                tmp = value[index]
                if isinstance(tmp, dict):
                    value[index] = json_to_bson(tmp)
                elif type(tmp) == str:
                    if re.match(r'^[0-9 a-f]{24}$', tmp) is not None:
                        value[index] = ObjectId(tmp)
                    elif re.match(r'^D:([0-9]*)$', tmp) is not None:
                        value[index] = time.time()
                    else:
                        pass
        elif isinstance(value, dict):
            obj[name] = json_to_bson(value)
    return obj


json_bson = json_to_bson


class MongoDatabase(IService):
    def config(self, conf):
        self.url = 'mongodb://{0}:{1}/{2}'.format(conf.get("host"), conf.get("port"), conf.get("database"))
        self.client = MongoClient(self.url)
        self.db = self.client.get_database()

    def __init__(self, name):
        IService.__init__(self, name)
        self.client = None
        self.url = None
        self.db = None

    def new_id(self):
        return ObjectId()

    def start(self, dance):
        pass

    def stop(self):
        self.db = None
        self.client.close()

    def delete_one(self, name, query):
        collection = self.db.get_collection(name)
        query = json_bson(query)
        return collection.delete_one(query)

    def delete_many(self, name, query):
        collection = self.db.get_collection(name)
        return collection.delete_many(query)

    def find(self, name, query: dict, order_by: dict=None, skip=0, limit=999, projection=None):
        collection = self.db.get_collection(name)
        query = json_bson(query)
        result = []
        if order_by is None:
            tmp = collection.find(query, projection).skip(skip).limit(limit)
        elif len(order_by.keys()) == 0:
            tmp = collection.find(query, projection).skip(skip).limit(limit)
        else:
            key, value = order_by.popitem()
            tmp = collection.find(query, projection).sort(key, value).skip(skip).limit(limit)

        for item in tmp:
            result.append(item)
        return result

    def find_one(self, name, query: dict):
        collection = self.db.get_collection(name)
        query = json_bson(query)
        return collection.find_one(
            query
        )

    def insert_or_update(self, name, query: dict, set_data: dict):
        collection = self.db.get_collection(name)
        query = json_bson(query)
        set_data = json_bson(set_data)
        collection.update(query, set_data, upsert=True)

    def insert(self, name, doc):
        collection = self.db.get_collection(name)
        collection.insert_one(
            json_bson(doc)
        )
        return doc

    def save(self, name, set_data: dict):
        collection = self.db.get_collection(name)
        if set_data.get('_id') is None:
            set_data['_id'] = self.new_id()
            self.insert(name, set_data)
        else:
            _id = set_data['_id']
            data = set_data.copy()
            del data['_id']
            self.update_one(name, {'_id': _id}, {'$set': data})
        return set_data

    def update_one(self, name, query, update):
        collection = self.db.get_collection(name)
        collection.update_one(json_bson(query), json_bson(update))

    def update_set_one(self, name, doc, fields):
        collection = self.db.get_collection(name)
        set_doc = {}
        for name in fields:
            value = doc.get(name)
            if value is not None:
                set_doc[name] = value

        collection.update_one({
            '_id': doc['_id']
        },
            set_doc
        )

    def size(self, name, query: dict):
        collection = self.db.get_collection(name)
        return collection.find(json_bson(query)).count()