from sqlalchemy import Column, String

from podcast.dao.base import BaseDao

# 定义User对象:
from podcast.pkg.client.mysql import session_scope


class User(BaseDao):
    __tablename__ = 'users'

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

    def __init__(self, **kwargs):
        self.gid = kwargs.get("gid")
        self.name = kwargs.get("name")
        self.email = kwargs.get("email")

    def save(self):
        with session_scope() as session:
            session.add(self)
        return self

    def get_user_by_email(self):
        with session_scope() as session:
            return session.query(User).filter(User.email == self.email).first()

    def get_user_by_gid(self):
        with session_scope() as session:
            return session.query(User).filter(User.gid == self.gid).first()

    def get_user_total(self) -> int:
        with session_scope() as session:
            return session.query(User).count()
        return 0