import inspect
import os
from abc import ABCMeta, abstractmethod
from dance.mq_message import MQMessage

COPY_KEYS = ['head', 'resource']


class MQHandler(metaclass=ABCMeta):
    def __init__(self, dance, packet):
        self.dance = dance
        self.packet = packet
        self.caller = packet.caller
        self.matrix = packet.matrix
        self.device = packet.device
        self.resource = packet.resource
        self.action = packet.action
        self.payload = packet.payload
        self.time = packet.time

    def find_postoffice(self, matrix, device):
        return self.dance.session.find_postoffice(matrix, device)

    def get_session(self, key, default=None):
        result = self.dance.session.get_value(self.matrix, self.device, key)
        if result is None:
            return default
        return result

    def clear_session(self):
        self.dance.session.clear(self.matrix, self.device)

    def set_session(self, key, value):
        self.dance.session.set_value(self.matrix, self.device, key, value)

    def work(self, resource, action, payload=bytes(0)):
        msg = MQMessage()
        msg.caller = self.caller
        msg.matrix = self.matrix
        msg.device = self.device
        msg.resource = resource
        msg.action = action
        msg.payload = payload
        self.dance.packet_arrive(msg)

    def reply(self, payload=bytes(0), resource=None, action=None):
        if resource is None:
            resource = self.resource
        if action is None:
            action = '_' + self.action
        MQHandler.send(self, self.caller, resource, action, payload)

    def send(self, topic, resource, action, payload):
        msg = MQMessage()
        msg.caller = self.dance.caller
        msg.matrix = self.matrix
        msg.device = self.device
        msg.resource = resource
        msg.action = action
        msg.payload = payload
        self.dance.send(topic, msg)
