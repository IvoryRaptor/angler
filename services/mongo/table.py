import re
import time
from bson import ObjectId


def json_bson_object_id(obj):
    for name in obj:
        value = obj[name]
    if type(value) == str:
        if re.match(r'^[0-9 a-f]{24}$', value) is not None:
            obj[name] = ObjectId(value)
        elif re.match(r'^D:([0-9]*)$', value) is not None:
            obj[name] = time.time()
        elif value[0] == '/':
            obj[name] = re(value.substring(1))
        else:
            pass
    elif isinstance(value, list):
        for index in range(len(value)):
            tmp = value[index]
            if isinstance(tmp, dict):
                value[index] = json_bson_object_id(tmp)
            elif re.match(r'^[0-9 a-f]{24}$', tmp):
                value[index] = ObjectId(value)
    elif isinstance(value, dict):
        json_bson_object_id(value)
    return obj


def json_bson_id_only(obj):
    for name in obj:
        value = obj[name]
    if name == '_id':
        obj[name] = ObjectId(value)
    if type(value) == str:
        if re.match(r'^D:([0-9]*)$', value) is not None:
            obj[name] = time.time()
        elif value[0] == '/':
            obj[name] = re(value.substring(1))
        else:
            pass
    elif isinstance(value, list):
        for index in range(len(value)):
            tmp = value[index]
            if isinstance(tmp, dict):
                value[index] = json_bson_id_only(tmp)
            elif re.match(r'^[0-9 a-f]{24}$', tmp):
                value[index] = ObjectId(value)
    elif isinstance(value, dict):
        json_bson_id_only(value)
    return obj


json_bson = json_bson_id_only


class MongoTable(object):
    def __init__(self, name, init, simple_fields):
        self.database = None
        self.name = name
        self.init = {}

        def new_id():
            return ObjectId()

        for field in init:
            value = init[field]
            if value == 'new_id()':
                self.init[field] = new_id
            else:
                def default_value():
                    return value
                self.init[field] = default_value

        self.simple_fields = simple_fields
        self.collection = None

    def simple(self, doc):
        result = {}
        for field in self.simple_fields:
            result[field] = doc.get(field)
        return result




