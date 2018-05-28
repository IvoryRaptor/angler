from tornado.websocket import WebSocketHandler
from angler.source import ASource
import logging
import random
import traceback


class SocketHandler(WebSocketHandler):
    def __init__(self, application, request):
        WebSocketHandler.__init__(self, application, request)
        self.id = str(random.random())[2:]

    def check_origin(self, origin):
        return True

    def on_close(self):
        del self.application.source.channels[self.id]

    def open(self):
        self.application.source.channels[self.id] = self

    def data_received(self, chunk):
        return True

    def on_message(self, message):
        packet = self.application.source.protocol.parse(message)
        logging.info('In %s ', packet)
        if packet is not None:
            try:
                self.application.angler.packet_arrive({
                    'host': 'self',
                    'actor': self.id,
                    'payload': packet
                })
            except Exception as err:
                logging.error('%s %s', err, traceback.format_exc())


class WebSocketSource(ASource):
    def __init__(self, name, protocol):
        ASource.__init__(self, name, protocol)
        self.channels = {}
        self.angler = None

    def config(self, conf):
        pass

    def get_source(self):
        return 'ws'

    def send(self, topic, packet):
        actor = packet['actor']
        channel = self.channels.get(actor)
        logging.info('Out [%s] => %s ', actor, packet)
        if channel is not None:
            data = self.protocol.serialize(packet['payload'])
            channel.write_message(data)
            self.angler.packet_arrive({
                'host': 'self',
                'actor': actor,
                'payload': packet.get('payload')
            })

    def stop(self):
        pass

    def start(self, angler):
        self.angler = angler
        app = angler.router.application
        app.add_handlers(
            r".*",
            [('/ws', SocketHandler),
             ]
        )
        app.source = self
        app.angler = angler
