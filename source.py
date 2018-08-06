from abc import ABCMeta, abstractmethod

from dance.protocol import AProtocol
from dance.service import IService


class ASource(IService):
    __metaclass__ = ABCMeta

    def __init__(self, name, protocol: AProtocol):
        IService.__init__(self, name)
        self.protocol = protocol
        self.container = None
        self.host = None

    @abstractmethod
    def start(self, dance):
        self.host = dance.host
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def send(self, source, packet):
        pass

    def arrive_packet(self, packet):
        self.container.packet_arrive(packet, [])


