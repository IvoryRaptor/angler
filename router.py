from functools import partial

from dance.service import IService


class Router(IService):
    def __init__(self):
        IService.__init__(self, 'router')
        self.dance = None
        self.matrixs = {}

    def stop(self):
        pass

    def get_topics(self, matrix, event):
        m = self.matrixs.get(matrix)
        if m is None:
            return []
        return m.get(event, [])

    def start(self, dance):
        self.dance = dance

        def watch_topics(m, name, events):
            m[name] = events

        def watch_event(matrix, evnets):
            m = self.matrixs[matrix]
            for event in evnets:
                e = m.get(event)
                if e is None:
                    watch = partial(watch_topics, m, event)
                    self.dance.sync.watch('/iotnn/{0}/{1}'.format(matrix, event), watch)

        def watch_matrix(evnets):
            for matrix in evnets:
                m = self.matrixs.get(matrix)
                if m is None:
                    m = {}
                    self.matrixs[matrix] = m
                    watch = partial(watch_event, matrix)
                    self.dance.sync.watch('/iotnn/{0}'.format(matrix), watch)
        self.dance.sync.watch('/iotnn/', watch_matrix)

    def config(self, conf):
        pass
