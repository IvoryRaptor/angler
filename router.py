from functools import partial

from dance.service import IService


class Router(IService):
    def __init__(self):
        IService.__init__(self, 'router')
        self.dance = None
        self.events = {}

    def stop(self):
        pass

    def get_topics(self, event):
        m = self.events.get(event)
        if m is None:
            return []
        return m

    def start(self, dance):
        self.dance = dance

        def watch_topics(event, topics):
            self.events[event] = topics

        def watch_events(events):
            for event in events:
                m = self.events.get(event)
                if m is None:
                    m = {}
                    self.events[event] = m
                    self.dance.sync.watch(
                        '/iotnn/{0}/{1}/{2}'.format(self.dance.matrix, self.dance.name, event),
                        partial(watch_topics, event)
                    )
        self.dance.sync.watch('/iotnn/{0}/{1}'.format(self.dance.matrix, self.dance.name), watch_events)

    def config(self, conf):
        pass
