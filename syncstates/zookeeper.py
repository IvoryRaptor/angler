from kazoo.client import KazooClient
from angler.service import IService
from kazoo.recipe.watchers import ChildrenWatch


class ZookeeperSync(IService):
    def __init__(self):
        IService.__init__(self, 'zookeeper')
        self.zk = None
        self.angler = None

    def stop(self):
        self.zk.stop()

    def start(self, angler):
        self.angler = angler
        self.zk.start()

    def config(self, conf):
        self.zk = KazooClient('{0}:{1}'.format(conf['host'], conf['port']))

    def watch(self, path, func):
        ChildrenWatch(self.zk, path, func)

    def register(self, path, value=None):
        self.logger.info('sync path %s', path)
        self.zk.ensure_path(path)
        self.zk.set(path, value)
