import time
from datetime import datetime

from pytz import timezone
from sqlalchemy import Column, Integer, TIMESTAMP, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy_utils import force_instant_defaults

from podcast.pkg.gid.global_id import get_gid
from podcast.pkg.ctx import Context
from podcast.pkg.type import camel

Base = declarative_base()


force_instant_defaults()


class GenStatus:
    Created = 100
    RUNNING = 200
    FAILED =  300
    FINISH = 1000

# 定义User对象:
class BaseDao(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    gid = Column(String(64), nullable=False, default=get_gid)
    created_by = Column(Integer, default=lambda: Context.get_user_id())
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: int(time.time()))
    updated_by = Column(Integer, default=lambda: Context.get_user_id(),
                        onupdate=lambda: Context.get_user_id())
    updated_at = Column(TIMESTAMP, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))
    is_deleted = Column(Boolean, default=0)

    def __iter__(self):
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            key = camel(column.name)
            if key == "gid":
                key = "id"
            if value is None:
                continue
            
            yield(key, value)
