import inspect
import os
from abc import ABCMeta, abstractmethod
from angler.mq_message import MQMessage

COPY_KEYS = ['head', 'resource']


class MQHandler(metaclass=ABCMeta):
    def __init__(self, angler, packet):
        self.angler = angler
        self.packet = packet

        self.source = packet.source
        self.destination = packet.destination

        self.matrix = packet.destination.matrix
        self.device = packet.destination.device
        self.resource = packet.resource
        self.action = packet.action
        self.payload = packet.payload

    def find_postoffice(self, matrix, device):
        return self.angler.session.find_postoffice(matrix, device)

    def get_session(self, key, default=None):
        result = self.angler.session.get_value(self.matrix, self.device, key)
        if result is None:
            return default
        return result

    def clear_session(self):
        self.angler.session.clear(self.matrix, self.device)

    def set_session(self, key, value):
        self.angler.session.set_value(self.matrix, self.device, key, value)

    def work(self, resource, action, payload=bytes(0)):
        msg = MQMessage()
        msg.source.matrix = self.source.matrix
        msg.source.device = self.source.device
        msg.destination.matrix = self.destination.matrix
        msg.destination.device = self.destination.device
        msg.resource = resource
        msg.action = action
        msg.payload = payload
        self.angler.packet_arrive(msg)

    def reply(self, payload=bytes(0), resource=None, action=None):
        if resource is None:
            resource = self.resource
        if action is None:
            action = '_' + self.action
        msg = MQMessage()
        msg.source.matrix = self.destination.matrix
        msg.source.device = self.destination.device
        msg.destination.matrix = self.source.matrix
        msg.destination.device = self.source.device
        msg.resource = resource
        msg.action = action
        msg.payload = payload
        self.send(msg)

    def out(self, resource, action, payload=bytes(0)):
        msg = MQMessage()
        msg.source.matrix = self.destination.matrix
        msg.source.device = self.destination.device
        msg.resource = resource
        msg.action = action
        msg.payload = payload
        return self.angler.out(msg)

    def send(self, msg):
        self.angler.send(msg)

    def check(self, msg):
        return True
