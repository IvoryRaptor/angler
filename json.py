import json
from bson import ObjectId
from datetime import datetime


class AnglerJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return ""
        return json.JSONEncoder.default(self, o)


encoder = AnglerJSONEncoder()

class JSONDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict2object)

    def dict2object(self, obj):
        # for key in obj.keys():
            # value = obj[key]
            # if type(value) == dict:
            #     print(value)
        return obj
#
#
# class JsonProtocol(AProtocol):
#     def serialize(self, packet):
#         return json.dumps(packet, cls=JSONEncoder)
#
#     def parse(self, data):
#         try:
#             return json.loads(data, cls=JSONDecoder)
#         except:
#             return None
