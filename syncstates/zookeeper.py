from kazoo.client import KazooClient
from angler.service import IService
from kazoo.recipe.watchers import ChildrenWatch


class ZookeeperSync(IService):
    def __init__(self):
        IService.__init__(self, 'zookeeper')
        self.zk = None
        self.angler = None
        self.funcs = []
        self.index = None
        self.master = False
        self.uri = None

    def stop(self):
        self.zk.stop()

    def start(self, angler):
        self.angler = angler
        self.zk.start()
        path = '/angler/{0}/{1}/'.format(self.angler.matrix, self.angler.name)
        name = self.zk.create(
            path,
            ephemeral=True,
            sequence=True,
            makepath=True
        )
        self.index = name[name.rindex('/') + 1:]

        def run_watch(nodes):
            nodes.sort()
            self.master = nodes[0] == self.index
            if self.master:
                for func in self.funcs:
                    func()
        self.watch(path, run_watch)

    def config(self, conf):
        self.uri = '{0}:{1}'.format(conf['host'], conf['port'])
        self.zk = KazooClient(self.uri)

    def watch(self, path, func):
        ChildrenWatch(self.zk, path, func)

    def master_func(self, func):
        self.funcs.append(func)
        if self.master:
            func()

    def register(self, path, value=None):
        self.logger.info('sync path %s', path)
        self.zk.ensure_path(path)
        self.zk.set(path, value)
