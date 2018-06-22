from angler.handlers import MQHandler
from angler.mq_message import MintPayload


class MintMQ(MQHandler):
    def heart(self):
        payload = MintPayload()
        payload.matrix = self.angler.matrix
        payload.angler = self.angler.name
        payload.number = self.angler.number
        payload.time = self.time
        data = payload.encode_to_bytes()
        self.reply(data)
