from abc import ABCMeta, abstractmethod
from dance.mq_message import MQMessage


class AProtocol(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, data):
        pass

    @abstractmethod
    def serialize(self, packet):
        pass


class ProtoBufProtocol(AProtocol):
    def serialize(self, packet):
        return packet.encode_to_bytes()

    def parse(self, data):
        try:
            ms = MQMessage()
            ms.parse_from_bytes(data)
            return ms
        except BaseException as err:
            print(err)
            return None
