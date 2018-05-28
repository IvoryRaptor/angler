import json

from angler.handlers.handler import MQHandler
from angler.mq_message import MQMessage
from angler.json import AnglerJSONEncoder


class MQJsonHandler(MQHandler):
    def __init__(self, angler, packet):
        MQHandler.__init__(self, angler, packet)
        payload={}
        try:
            payload = json.loads(packet.payload.decode("utf-8"))
        except:
            pass
        self.callback = payload.get('callback')
        self.payload = payload.get('payload', {})

    def reply(self, payload,resource= None, action= None):
        if resource is None:
            resource = self.resource
        if action is None:
            action = '_' + self.action
        payload = {
            'payload': payload
        }
        MQHandler.reply(self, resource, action, bytes(json.dumps(payload, cls=AnglerJSONEncoder), encoding="utf8"))

        # dict1base64file2dict(
        #     self.payload,
        #     self.angler.upload_static_path,
        #     self.angler.web_server_static_url)

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
    #     msg.payload = bytes(json.dumps(payload, cls=AnglerJSONEncoder), encoding="utf8")
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
