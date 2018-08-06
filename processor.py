import json
import os
import re

from dance.service import IService
from dance.handlers.handler import MQHandler
from dance.resources.mint import MintMQ
from tornado.web import RequestHandler
import tornado
import inspect


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self)
        self.dance = None

    def bind_dance(self, dance):
        self.dance = dance

class Processor(IService):
    def __init__(self):
        IService.__init__(self, 'process')
        self.dance = None
        self.handlers = {}
        self.application = Application()
        self.server = None

    def config(self, conf):
        pass

    def add_mq(self, handler, mq_class):
        if handler not in self.handlers.keys():
            self.handlers[handler] = []
        self.handlers[handler].append(mq_class)
        self.logger.info('Add MQ {0} {1}'.format(handler, mq_class))

    def add_web(self, pattern, handler, path=None):
        process_array = [('/' + pattern, handler)]
        self.application.add_handlers(
            r".*",
            process_array
        )

    def stop(self):
        if self.server is not None:
            self.server.stop()

    def work(self, packet):
        handler = '{0}.{1}'.format(packet.resource, packet.action)
        self.logger.info(handler)

        if handler in self.handlers.keys():
            for mq_class in self.handlers[handler]:
                worker = mq_class(self.dance, packet)
                getattr(worker, packet.action)()
            return True
        return False

    def get_getattr(self, path):
        sp = path.split('.')
        model_name = ''
        for index in range(len(sp) - 1):
            model_name = model_name + sp[index] + '.'
        model_name = model_name[0:len(model_name) - 1]
        model = __import__(model_name)
        result = model

        for index in range(len(sp) - 1):
            result = getattr(result, sp[index + 1], None)
        return result

    def get_messages(self, path):
        result = []
        base_invoke = dir(MQHandler)
        base_namespace = path.replace('/', '.')
        for sub_path in os.listdir(path):
            if re.match('^[a-z][a-z|_]+$', sub_path):
                self.dance.sync.register('{0}/{1}'.format(path, sub_path))
            elif re.match('^[a-z|_]+.py$', sub_path):
                namespace = sub_path[0:-3]
                sp = namespace.split('_')
                class_name = ''
                for v in sp:
                    class_name = class_name + v[0].upper() + v[1:]
                self.logger.info('{0}.{1}.{2}MQ'.format(base_namespace, namespace, class_name))
                mq_class = self.get_getattr('{0}.{1}.{2}MQ'.format(base_namespace, namespace, class_name))
                if mq_class is not None:
                    for item in inspect.getmembers(mq_class):
                        if (
                                item[0] not in base_invoke
                                and inspect.signature(item[1]).parameters.__len__() == 1
                        ):
                            result.append('{0}.{1}'.format(
                                    namespace, item[0]))
        return result
                            # self.dance.sync.register(
                            #     'iotnn/postoffice/{0}/{2}.{3}/{0}_{1}'.format(
                            #         self.dance.matrix, self.dance.name, namespace, item[0])
                            # )

    def add_system_router(self, mq):
        self.logger.info('Add System Router')
        namespace = mq.__name__[0:-2].lower()
        base_invoke = dir(MQHandler)
        self.add_mq('mint', MintMQ)
        for event in list(set(dir(mq)).difference(set(base_invoke))):
            self.add_mq('{0}.{1}'.format(namespace, event), mq)

    def add_router(self, path):
        self.logger.info('Add Router %s', path)
        base_invoke = dir(MQHandler)
        base_namespace = path.replace('/', '.')
        for sub_path in os.listdir(path):
            if re.match('^[a-z][a-z|_]+$', sub_path):
                self.add_router('{0}/{1}'.format(path, sub_path))
            elif re.match('^[a-z|_]+.py$', sub_path) and sub_path != '__init__.py':
                namespace = sub_path[0:-3]
                sp = namespace.split('_')
                class_name = ''
                for v in sp:
                    class_name = class_name + v[0].upper() + v[1:]
                mq_class = self.get_getattr('{0}.{1}.{2}MQ'.format(base_namespace, namespace, class_name))
                self.logger.info('Add %s.%s.%sMQ', base_namespace, namespace, class_name)
                if mq_class is not None:
                    for event in list(set(dir(mq_class)).difference(set(base_invoke))):
                        self.add_mq('{0}.{1}'.format(namespace, event), mq_class)
                tmp = self.get_getattr('{0}.{1}.{2}Web'.format(base_namespace, namespace, class_name))
                if tmp is not None:
                    self.add_web(namespace, tmp)

    def start(self, dance):
        self.dance = dance
        self.application.bind_dance(dance)

        result = json.dumps(self.get_messages('resources'))

        class IOTNNHandler(RequestHandler):
            def data_received(self, chunk):
                pass

            def get(self):
                self.write(result)

        self.application.add_handlers(
            r".*",
            [(r'/iotnn', IOTNNHandler),
             (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': dance.get_config('upload_static_path')})
             ]
        )
        self.add_system_router(MintMQ)
        self.add_router('resources')

        # self.register_sync('resources')
        web_port = dance.get_config('web_port')
        if web_port is not None:
            self.server = self.application.listen(web_port, '0.0.0.0')
