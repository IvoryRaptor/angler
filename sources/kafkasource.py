import _thread
import datetime
import traceback
from time import sleep
from kafka import KafkaProducer, KafkaConsumer
from angler.source import ASource


class KafkaSource(ASource):
    def __init__(self, name, protocol):
        ASource.__init__(self, name, protocol)
        self.uri = None
        self.producer = None
        self.group = None
        self.running = False
        self.topic = None
        self.consumer = None

    def config(self, conf):
        self.uri = '{0}:{1}'.format(conf['host'], conf.get('port', 9092))
        self.topic = conf['query']
        self.group = conf.get('group')

    def send(self, topic, msg):
        self.logger.info(
            'Out [%s] %s/%s =>%s/%s %s.%s',
            topic,
            msg.source.matrix,
            msg.source.device,
            msg.destination.matrix,
            msg.destination.device,
            msg.resource,
            msg.action
        )
        data = self.protocol.serialize(msg)
        if data is not None:
            self.producer.send(topic, data)

    def start(self, angler):
        self.running = True
        self.producer = KafkaProducer(bootstrap_servers=self.uri)
        consumer = KafkaConsumer(bootstrap_servers=self.uri,
                                 group_id=self.group,
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe([self.topic])
        self.consumer = consumer

        def callback():
            while self.running:
                for message in consumer:
                    packet = self.protocol.parse(message.value)
                    self.logger.info(
                        'In %s/%s=>%s/%s %s.%s',
                        packet.source.matrix,
                        packet.source.device,
                        packet.destination.matrix,
                        packet.destination.device,
                        packet.resource,
                        packet.action
                    )
                    if packet is not None:
                        try:
                            angler.packet_arrive(packet)
                        except Exception as err:
                            self.logger.error('%s %s', err, traceback.format_exc())
                sleep(1)
            consumer.close()

        _thread.start_new_thread(callback, ())

    def stop(self):
        self.consumer.unsubscribe()
        self.running = False
