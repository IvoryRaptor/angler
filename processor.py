import json
import os
import re

from dance.service import IService
from dance.handlers.handler import MQHandler
from dance.resources.mint import MintMQ
from dance.helper import load_yaml_file
from tornado.web import RequestHandler
import tornado
import inspect
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self)
        self.dance = None

    def bind_dance(self, dance):
        self.dance = dance


class WatchHandler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor

    def on_modified(self, event):
        if not os.path.exists('config/processor/config.yaml'):
            self.processor.turnouts = {}
            return
        tmp = load_yaml_file('config/processor/config.yaml')
        if not isinstance(self.processor.turnouts, dict):
            self.processor.turnouts = {}
            return
        turnouts = {}
        for key in tmp:
            mqs = []
            for mq in tmp[key]:
                sp = mq.split('_')
                mq = mq + '.'
                for item in sp:
                    mq = mq + item[0].upper() + item[1:]
                mq = mq + 'MQ'
                print('-------' + mq)
                mqs.append(mq)
            turnouts[key] = mqs
        self.processor.turnouts = turnouts
        self.processor.logger.info('turnouts: ', self.processor.turnouts)


class Processor(IService):
    def __init__(self):
        IService.__init__(self, 'process')
        self.hclass = {}
        self.dance = None
        self.handlers = {}
        self.turnouts = {}
        self.application = Application()
        self.server = None
        self.observer = Observer()
        watch = WatchHandler(self)
        watch.on_modified(None)
        if os.path.exists('config/processor'):
            self.observer.schedule(watch, 'config/processor', recursive=True)

    def config(self, conf):
        pass

    def add_class(self, class_name, mq_class):
        print('*****' + class_name)
        self.hclass[class_name] = mq_class

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
        self.observer.stop()
        if self.server is not None:
            self.server.stop()

    def work(self, packet):
        handler = '{0}.{1}'.format(packet.resource, packet.action)
        self.logger.info(handler)
        result = False
        if handler in self.turnouts.keys():
            for class_name in self.turnouts[handler]:
                print(class_name, self.hclass.keys(), handler)
                mq_class = self.hclass[class_name]
                worker = mq_class(self.dance, packet)

                getattr(worker, handler.split('.')[1])()
                result = result or True

        if handler in self.handlers.keys():
            for mq_class in self.handlers[handler]:
                worker = mq_class(self.dance, packet)
                getattr(worker, packet.action)()
                result = result or True
        return result

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
            if re.match('^[a-z|_]+.py$', sub_path):
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
                    self.add_class('{0}.{1}MQ'.format(namespace, class_name), mq_class)
                    self.logger.info('Add class {0}.{1}MQ'.format(namespace, class_name))

                    for event in list(set(dir(mq_class)).difference(set(base_invoke))):
                        self.add_mq('{0}.{1}'.format(namespace, event), mq_class)
                tmp = self.get_getattr('{0}.{1}.{2}Web'.format(base_namespace, namespace, class_name))
                if tmp is not None:
                    self.add_web(namespace, tmp)

    def start(self, dance):
        self.dance = dance
        self.application.bind_dance(dance)
        self.observer.start()

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
