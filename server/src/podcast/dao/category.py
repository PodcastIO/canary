from sqlalchemy import Column, String
from podcast.pkg.ctx import Context

from podcast.pkg.client.mysql import session_scope
from podcast.dao.base import BaseDao


class Category(BaseDao):
    __tablename__ = 'categories'

    name = Column(String(64), nullable=False)

    def __init__(self, **kwargs):
        BaseDao.__init__(self)
        self.name = kwargs.get("name", "default")

    def save(self):
        with session_scope() as session:
            session.add(self)
            return self

    def update(self):
        with session_scope() as session:
            session.query(Category).filter(Category.gid == self.gid).\
                filter(Category.created_by == Context.get_user_id()).update({
                    "name": self.name,
                })

    @classmethod
    def get_all(cls):
        with session_scope() as session:
            return session.query(Category).all()

    def get_by_gid(self):
        if self.gid == "0":
            self.name = "default"
            return self
        
        with session_scope() as session:
            self = session.query(Category).filter(Category.gid == self.gid).\
                filter(Category.created_by == Context.get_user_id()).one()
            return self
