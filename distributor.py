import os

from dance.service import IService
from dance.helper import load_yaml_file
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import copy


class WatchHandler(FileSystemEventHandler):
    def __init__(self, distributor):
        self.distributor = distributor

    def on_modified(self, event):
        if not os.path.exists('config/distributor/config.yaml'):
            self.distributor.distributes = {}
            return
        conf = load_yaml_file('config/distributor/config.yaml')
        if not isinstance(conf, dict):
            self.distributor.distributes = {}
        else:
            for handler in conf.keys():
                self.distributor.distributes[handler] = []
                for item in conf[handler]:
                    self.distributor.distributes[handler].append(item.split('.'))


class Distributor(IService):
    def __init__(self):
        IService.__init__(self, 'distributor')
        self.distributes = {}
        self.observer = Observer()
        watch = WatchHandler(self)
        watch.on_modified(None)
        if os.path.exists('config/distributor'):
            self.observer.schedule(watch, 'config/distributor', recursive=True)

    def dis_packet(self, packet):
        tmp = self.distributes.get('{0}.{1}'.format(packet.resource, packet.action))
        if tmp is None:
            return None
        result = []
        for item in tmp:
            np = copy.copy(packet)
            np.resource = item[0]
            np.action = item[1]
            result.append(np)
        return result

    def stop(self):
        self.observer.stop()

    def start(self, dance):
        self.observer.start()

    def config(self, conf):
        pass
