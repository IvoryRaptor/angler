import json

from dance.service import IService
from dance.json import DanceJSONEncoder
from redis import Redis


class Session(IService):
    def config(self, conf):
        self.redis = Redis(host=conf['host'], port=int(conf['port']), db=0)

    def __init__(self):
        IService.__init__(self, 'session')
        self.redis = None
        self.dance = None
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
        self.redis.hset(full_actor, key, json.dumps(value, cls=DanceJSONEncoder))

    def start(self, dance):
        self.dance = dance
        self.channel_key = 'SYSTEM_CHANNEL' + dance.project
        self.matrix_list = 'SYSTEM_MATRIX' + dance.matrix

    def stop(self):
        pass
