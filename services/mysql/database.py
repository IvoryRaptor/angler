import imp
import sys

from bson import ObjectId
from sqlalchemy import Column, String, create_engine, ForeignKey, Integer, DateTime, update
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

from angler.service import IService


class MySqlDatabase(IService):
    def __init__(self, name=None, url=None):
        IService.__init__(self, name)
        self.url = url
        self.engine = None
        self.DBSession = None

    def config(self, conf):
        self.url = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}' \
            .format(conf.get("destination"), conf.get("password"), conf.get("ip"), conf.get("port"), conf.get("dbname"))

    @staticmethod
    def new_id():
        return str(ObjectId())

    def session(self):
        # return self.DBSession()

        # self.DBSession = scoped_session(sessionmaker(bind=self.engine,
        #                                              autocommit=False, autoflush=True,
        #                                              expire_on_commit=False))
        dbsessioon = self.DBSession()
        print(dbsessioon)
        return dbsessioon

    # def get_class(self, name):
    #     return getattr(self.mod, name)

    def start(self, angler):
        # self.engine = create_engine(self.url, pool_recycle=7200,connect_args={'connect_timeout': 10})
        # self.engine = create_engine(self.url, pool_recycle=True)
        self.engine = create_engine(self.url, pool_recycle=5)
        # 创建DBSession类型:
        # # self.DBSession = sessionmaker(bind=self.engine)
        self.DBSession = scoped_session(sessionmaker(bind=self.engine,
                                                     autocommit=False, autoflush=True,
                                                     expire_on_commit=False))

    def stop(self):
        pass
