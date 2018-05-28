import logging
from abc import ABCMeta, abstractmethod


class IService(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('angler.{0}'.format(name))

    @abstractmethod
    def config(self, conf):
        pass

    @abstractmethod
    def start(self, angler):
        pass

    @abstractmethod
    def stop(self):
        pass
