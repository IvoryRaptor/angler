from angler.handlers import MQHandler
from angler.mq_message import MintPayload


class MintMQ(MQHandler):
    def heart(self):
        payload = MintPayload()
        payload.partition = self.payload[0]
        payload.number = self.angler.number
        payload.time = self.time
        data = payload.encode_to_bytes()
        self.reply(data)
