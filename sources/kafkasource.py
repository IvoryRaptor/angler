import _thread
import traceback
from time import sleep
from pykafka import KafkaClient
from dance.source import ASource


class KafkaSource(ASource):
    def __init__(self, name, protocol):
        ASource.__init__(self, name, protocol)
        self.uri = None
        self.group = None
        self.running = False
        self.topic = None
        self.consumer = None
        self.client = None
        self.producers = {}

    def config(self, conf):
        self.uri = '{0}:{1}'.format(conf['host'], conf.get('port', 9092))
        self.topic = conf['query']
        self.group = conf.get('group')

    def send(self, topic_name, msg):
        data = self.protocol.serialize(msg)
        if data is not None:
            self.logger.info(
                'Out [%s] %s/%s => %s.%s',
                str(topic_name, encoding = "utf-8"),
                msg.matrix,
                msg.device,
                msg.resource,
                msg.action
            )
            producer = self.producers.get(topic_name)
            if producer is None:
                topic = self.client.topics[topic_name]
                producer = topic.get_sync_producer()
                self.producers[topic_name] = producer
            producer.produce(data)

    def start(self, dance):
        self.running = True
        self.client = KafkaClient(hosts=self.uri)

        topic = self.client.topics[bytes(self.topic, encoding='utf8')]
        self.consumer = topic.get_balanced_consumer(
            consumer_group=bytes(self.group, encoding='utf8'),
            auto_commit_enable=True,
            zookeeper_connect=dance.sync.uri
        )

        def callback():
            self.logger.info("Watch Topic=%s", self.topic)
            while self.running:
                for message in self.consumer:
                    packet = self.protocol.parse(message.value)
                    if packet is not None:
                        self.logger.info(
                            'In %d %s=>/%s/%s %s.%s',
                            packet.time,
                            packet.caller,
                            packet.matrix,
                            packet.device,
                            packet.resource,
                            packet.action,
                        )
                        try:
                            dance.packet_arrive(packet)
                        except Exception as err:
                            self.logger.error('%s %s', err, traceback.format_exc())
                    self.consumer.commit_offsets()
                sleep(1)
            self.consumer.close()
        _thread.start_new_thread(callback, ())

    def stop(self):
        self.consumer.close()
        self.running = False
