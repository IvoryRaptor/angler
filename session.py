import json

from angler.service import IService
from angler.json import AnglerJSONEncoder
from redis import Redis


class Session(IService):
    def config(self, conf):
        self.redis = Redis(host=conf['host'], port=int(conf['port']), db=0)

    def __init__(self):
        IService.__init__(self, 'session')
        self.redis = None
        self.angler = None
        self.channel_key = None
        self.matrix_list = None

    def find_postoffice(self, matrix, device):
        return self.redis.hget('POSTOFFICE', matrix + '/' + device)

    def clear(self, host, actor):
        full_actor = str(host) + '@' + actor
        self.redis.delete(full_actor)

    def get_value(self, host, actor, key, default=None):
        full_actor = str(host) + '@' + actor
        result = self.redis.hget(full_actor, key)
        if result is None:
            return default
        return json.loads(result)

    def set_value(self, host, actor, key, value):
        full_actor = str(host) + '@' + actor
        self.redis.hset(full_actor, key, json.dumps(value, cls=AnglerJSONEncoder))

    def start(self, angler):
        self.angler = angler
        self.channel_key = 'SYSTEM_CHANNEL' + angler.project
        self.matrix_list = 'SYSTEM_MATRIX' + angler.matrix

    def stop(self):
        pass
