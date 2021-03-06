import time
import sched
from dance.service import IService


class TimerDatabase(IService):
    def config(self, conf):
        pass

    def __init__(self):
        IService.__init__(self, "timer")
        self.schedule = sched.scheduler(time.time, time.sleep)

    def enter(self, delay, priority, action):
        self.schedule.enter(delay, priority, action)

    def start(self, dance):
        self.schedule.run()

    def stop(self):
        pass
