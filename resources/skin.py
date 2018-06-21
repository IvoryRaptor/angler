from angler.handlers import MQHandler
from angler.mq_message import SkinPayload


class SkinMQ(MQHandler):
    def heart(self):
        payload = SkinPayload()
        payload.matrix = self.angler.matrix
        payload.angler = self.angler.name
        payload.number = self.angler.number
        payload.time = self.time
        data = payload.encode_to_bytes()
        self.reply(data)
