import json

from dance.handlers.handler import MQHandler
from dance.json import DanceJSONEncoder


class MQJsonHandler(MQHandler):
    def __init__(self, dance, packet):
        MQHandler.__init__(self, dance, packet)
        payload = {}
        try:
            payload = json.loads(packet.payload.decode("utf-8"))
        except:
            pass
        self.callback = payload.get('callback')
        self.payload = payload.get('payload', {})

    def error(self, payload, resource=None, action=None):
        payload = {
            'error': payload
        }
        MQHandler.reply(self, bytes(json.dumps(payload, cls=DanceJSONEncoder), encoding="utf8"), resource, action)

    def send(self, topic, resource, action, payload):
        if isinstance(topic, str):
            topic = bytes(topic, encoding="utf-8")
        payload = {
            'payload': payload
        }
        MQHandler.send(self, topic, resource, action, bytes(json.dumps(payload, cls=DanceJSONEncoder), encoding="utf8"))

    def reply(self, payload, resource=None, action=None):
        payload = {
            'payload': payload
        }
        MQHandler.reply(self, bytes(json.dumps(payload, cls=DanceJSONEncoder), encoding="utf8"), resource, action)

        # dict1base64file2dict(
        #     self.payload,
        #     self.dance.upload_static_path,
        #     self.dance.web_server_static_url)

    # def write(self, payload, topic=None, host=None, actor=None, resource=None, action=None):
    #     msg = MQMessage()
    #     msg.host = host if host is not None else self.host
    #     msg.actor = actor if actor is not None else self.actor
    #     msg.resource = resource if resource is not None else self.resource
    #     msg.action = action if action is not None else '_' + self.action
    #     payload = {
    #         'payload': payload
    #     }
    #     if self.callback is not None:
    #         payload['callback'] = self.callback
    #     msg.payload = bytes(json.dumps(payload, cls=DanceJSONEncoder), encoding="utf8")
    #
    #     topic = topic if topic is not None else 'postoffice-{0}'.format(msg.host)
    #     MQHandler.write(self, topic, msg)
    #
    # def error(self, error, describe, topic=None, host=None, actor=None, resource=None, action=None):
    #     msg = MQMessage()
    #     topic = topic if topic is not None else 'postoffice-{0}'.format(host)
    #     msg.host = host if host is not None else self.host
    #     msg.actor = actor if actor is not None else self.actor
    #     msg.resource = resource if resource is not None else self.resource
    #     msg.action = action if action is not None else '_' + self.action
    #     payload = {
    #         'error': error,
    #         'describe': describe
    #     }
    #     if self.callback is not None:
    #         payload['callback'] = self.callback
    #     msg.payload = bytes(json.dumps(payload), encoding="utf8")
    #     MQHandler.write(self, topic, msg)
