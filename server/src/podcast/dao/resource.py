from sqlalchemy import Column, String
from podcast.pkg.ctx import Context

from podcast.pkg.client.mysql import session_scope
from podcast.dao.base import BaseDao


# 定义User对象:
class Resource(BaseDao):
    __tablename__ = 'resources'

    name = Column(String(128), nullable=False)
    resource_type = Column(String(64), nullable=False)

    def __init__(self, **kwargs):
        BaseDao.__init__(self)

        self.gid = kwargs.get("gid")
        self.name = kwargs.get("name", "")
        self.resource_type = kwargs.get("resource_type", "")

    def save(self):
        with session_scope() as session:
            session.add(self)

    @staticmethod
    def batch_save(resources):
        with session_scope() as session:
            for resource in resources:
                session.add(resource)

    def get_by_gid(self):
        with session_scope() as session:
            return session.query(Resource).filter(Resource.gid == self.gid).first()

    @classmethod
    def get_by_gid_array(cls, gid_array):
        with session_scope() as session:
            return session.query(cls).filter(Resource.gid.in_(gid_array)).all()
