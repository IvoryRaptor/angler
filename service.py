import logging
from abc import ABCMeta, abstractmethod


class IService(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('dance.{0}'.format(name))

    @abstractmethod
    def config(self, conf):
        pass

    @abstractmethod
    def start(self, dance):
        pass

    @abstractmethod
    def stop(self):
        pass
