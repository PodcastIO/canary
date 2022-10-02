import time
from typing import List
from sqlalchemy import Column, String, desc, Integer, Text
from podcast.pkg.ctx import Context

from podcast.pkg.client.mysql import session_scope
from podcast.dao.base import BaseDao
from podcast.pkg.cipher.jwt import Jwt
from urllib.parse import quote

from podcast.dao.base import GenStatus


class PodcastSource:
    local = 'Local'
    rss = 'RSS'
    video = 'Video'


class Frequency:
    hour = 'Hour'
    day = 'Day'
    week = 'Week'
    month = 'Month'


class Podcast(BaseDao):
    __tablename__ = 'podcasts'

    source = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    cover_resource_id = Column(String(64))
    book_resource_id = Column(String(64))
    gen_status = Column(Integer, nullable=False, default=int(GenStatus.Created))
    description = Column(Text)
    language = Column(String(64))
    share_enable = Column(Integer, default=0)
    share_time = Column(Integer, default=None)
    url = Column(String(256))
    frequency = Column(String(128))
    frequency_value = Column(Integer, nullable=False, default=1)
    first_execute_time = Column(Integer, default=None)
    timer_id = Column(String(256))
    share_token = Column(String(256))

    def __init__(self, **kwargs):
        BaseDao.__init__(self)
        self.gid = kwargs.get("gid")
        self.source = kwargs.get("source", "")
        self.title = kwargs.get("title", "")
        self.author = kwargs.get("author", "")
        self.cover_resource_id = kwargs.get("cover_resource_id", "")
        self.book_resource_id = kwargs.get("book_resource_id", "")
        self.rss = kwargs.get("rss", "")
        self.description = kwargs.get("description", "")
        self.language = kwargs.get("language", None)
        self.gen_status = kwargs.get("gen_status", None)
        self.share_time = kwargs.get("share_time", None)
        self.url = kwargs.get("url", None)
        self.frequency = kwargs.get("frequency", None)
        self.frequency_value = kwargs.get("frequency_value", None)
        self.first_execute_time = kwargs.get("first_execute_time", None)
        self.timer_id = kwargs.get("timer_id", None)
        self.share_enable = kwargs.get("share_enable", 0)
        self.share_token = kwargs.get("share_token", "")

    def get_share_token(self):
        if self.share_enable == 1:
            return quote(Jwt(payload={
                "podcast_id": self.gid,
                "share_time": self.share_time,
                "user_id": Context.get_user_id(),
            }).encode_share_token())
        return ""

    def save(self):
        with session_scope() as session:
            self.token = self.get_share_token()
            session.add(self)

    def update(self, value):
        with session_scope() as session:
            value.update({
                "share_token": self.get_share_token()
            })
            session.query(Podcast).filter(Podcast.gid == self.gid)\
                .filter(Podcast.created_by == Context.get_user_id())\
                .filter(Podcast.is_deleted == 0)\
                .update(value)

    def delete(self):
        with session_scope() as session:
            session.query(Podcast).filter(Podcast.gid == self.gid)\
                .filter(Podcast.created_by == Context.get_user_id())\
                .filter(Podcast.is_deleted == 0)\
                .update({
                    'is_deleted': 1,
                })

    @classmethod
    def get_podcasts(cls, offset: int, limit: int):
        if limit <= 0:
            return []
        
        if offset <= 0:
            offset = 0

        with session_scope() as session:
            podcasts = session.query(cls).filter(Podcast.created_by == Context.get_user_id())\
                .filter(Podcast.is_deleted == 0)\
                .order_by(desc(cls.created_at)).offset(offset).limit(limit).all()
            return podcasts

    @classmethod
    def get_podcasts_total(cls):
        with session_scope() as session:
            total = session.query(cls).filter(Podcast.created_by == Context.get_user_id())\
                .filter(Podcast.is_deleted == 0)\
                .count()
            return total

    def get_by_gid(self):
        with session_scope() as session:
            self = session.query(Podcast).filter(Podcast.gid == self.gid)\
                .filter(Podcast.created_by == Context.get_user_id())\
                .filter(Podcast.is_deleted == 0)\
                .first()
            return self
    
    @classmethod
    def get_by_gids(cls, gids: List[int]):
        with session_scope() as session:
            podcasts = session.query(Podcast)\
                .filter(Podcast.is_deleted == 0)\
                .filter(Podcast.gid.in_(gids)).all()
            return podcasts