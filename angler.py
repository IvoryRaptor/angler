import logging
import threading
import time

from tornado import ioloop
from apscheduler.schedulers.background import BackgroundScheduler
from angler.syncstates.zookeeper import ZookeeperSync
from angler.session import Session
from angler.sources.kafkasource import KafkaSource
from angler.sources.websocketsource import WebSocketSource
from angler.protocol import ProtoBufProtocol
from angler.processor import Processor
from angler.router import Router


class Angler:
    def __init__(self):
        self.logger = logging.getLogger('angler')
        self.name = ''
        self.matrix = ''
        self.project = ''
        self.services = []
        self.configs = None

        self.source = None
        self.session: Session = None
        self.processor = None
        self.sync = None
        self.routers = None

        self.io_thread = None
        self.scheduler = BackgroundScheduler()

    def get_config(self, name):
        return self.configs.get(name)

    def config(self, conf):
        self.configs = conf
        self.name = conf['angler']
        self.matrix = conf['matrix']
        self.project = conf['project']

        source_type = conf['source'].get('type')
        if source_type == 'websocket':
            self.source = WebSocketSource(
                'source',
                ProtoBufProtocol()
            )
        else:
            self.source = KafkaSource(
                'source',
                ProtoBufProtocol()
            )
        self.services.append(self.source)
        self.source.config(conf['source'])

        self.session = Session()
        self.session.config(conf['session'])
        self.services.append(self.session)

        sync_type = conf['sync'].get('type')
        if sync_type == 'zookeeper':
            self.sync = ZookeeperSync()
        self.sync.config(conf['sync'])
        self.services.append(self.sync)

        self.processor = Processor()
        self.services.append(self.processor)

        self.routers = Router()
        self.services.append(self.routers)

        if 'services' in conf.keys():
            services = __import__('services')
            for service_name in conf['services'].keys():
                service = getattr(services, service_name)
                service.config(conf['services'][service_name])
                self.services.append(service)

    def packet_arrive(self, packet):
        self.processor.work(packet)

    def add_job(self, *args, **other):
        self.scheduler.add_job(*args, **other)

    def remove_job(self, name):
        self.scheduler.remove_job(name)

    def out(self, msg):
        msg.destination.matrix = "POSTOFFICE"
        host = self.session.find_postoffice(msg.source.matrix, msg.source.device)
        if host is None:
            return None
        msg.destination.device = host
        self.source.send('postoffice-' + host, msg)

    def send(self, msg):
        if msg.destination.matrix == "POSTOFFICE":
            self.source.send('default.postoffice-' + msg.destination.device, msg)
            return
        for topic in self.sync.routers.get(msg.destination.matrix, msg.resource + '.' + msg.action):
            self.source.send(topic, msg)

    def start(self):
        for item in self.services:
            self.logger.info('start %s', item.name)
            item.start(self)
            self.logger.info('start %s complete', item.name)
        self.io_thread = threading.Thread(target=ioloop.IOLoop.instance().start, args=[])
        self.io_thread.start()
        self.scheduler.start()

    def master_func(self, func):
        self.sync.master_func(func)

    def stop(self):
        self.scheduler.shutdown()
        loop = ioloop.IOLoop.instance()
        loop.add_callback(loop.stop)

        self.io_thread.join()
        time.sleep(1)
        for item in self.services:
            item.stop()
