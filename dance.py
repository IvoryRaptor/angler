import logging
import threading
import time

from tornado import ioloop
from apscheduler.schedulers.background import BackgroundScheduler
from dance.syncstates.zookeeper import ZookeeperSync
from dance.session import Session
from dance.sources.kafkasource import KafkaSource
from dance.sources.websocketsource import WebSocketSource
from dance.protocol import ProtoBufProtocol
from dance.processor import Processor
from dance.router import Router
from dance.distributor import Distributor


class Dance:
    def __init__(self):
        self.logger = logging.getLogger('dance')
        self.name = ''
        self.matrix = ''
        self.number = ''
        self.project = ''
        self.caller = ''
        self.services = []
        self.configs = None

        self.source = None
        self.session: Session = None
        self.processor = None
        self.distributor = None
        self.sync = None
        self.routers = None

        self.io_thread = None
        self.scheduler = BackgroundScheduler()

    def get_config(self, name):
        return self.configs.get(name)

    def config(self, conf):
        self.configs = conf
        self.name = conf['dance']
        self.matrix = conf['matrix']
        self.project = conf['project']
        self.caller = conf['matrix'] + '_' + conf['dance']

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

        self.distributor = Distributor()
        self.services.append(self.distributor)

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
        ps = self.distributor.dis_packet(packet)
        if ps is None:
            if not self.processor.work(packet):
                self.logger.warning("Miss Packet %s.%s", packet.resource, packet.action)
        else:
            for packet in ps:
                if not self.processor.work(packet):
                    self.logger.warning("Miss Packet %s.%s", packet.resource, packet.action)

    def add_job(self, *args, **other):
        self.scheduler.add_job(*args, **other)

    def remove_job(self, name):
        self.scheduler.remove_job(name)

    def send(self, topic, msg):
        event = '{0}.{1}'.format(msg.resource, msg.action)
        for t in self.routers.get_topics(event):
            self.source.send(t, msg)
        if topic is not None:
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
