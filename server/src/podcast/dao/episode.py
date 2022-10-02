from typing import List

from sqlalchemy import Column, String, Text, Integer, desc

from podcast.pkg.client.mysql import session_scope
from podcast.dao.base import BaseDao


from podcast.pkg.ctx import Context
from podcast.dao.base import GenStatus


class Episode(BaseDao):
    __tablename__ = 'episodes'

    podcast_gid = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    voice_resource_id = Column(String(64))
    episode_size = Column(Integer, nullable=False, default=0)
    key = Column(String(255))
    link = Column(String(512))
    cover_resource_id = Column(String(64))
    pub_time = Column(Integer)
    gen_status = Column(Integer, default=int(GenStatus.Created))

    def __init__(self, **kwargs):
        BaseDao.__init__(self)

        self.gid = kwargs.get("gid")
        self.podcast_gid = kwargs.get("podcast_gid")
        self.title = kwargs.get("title")
        self.content = kwargs.get("content")
        self.order = kwargs.get("order")
        self.voice_resource_id = kwargs.get("voice_resource_id")
        self.episode_size = kwargs.get("episode_size")
        self.key = kwargs.get("key")
        self.link = kwargs.get("link")
        self.cover_resource_id = kwargs.get("cover_resource_id")
        self.pub_time = kwargs.get("pub_time")
        self.gen_status = kwargs.get("gen_status")

    @classmethod
    def save(cls, episodes):
        with session_scope() as session:
            session.add_all(episodes)

    @staticmethod
    def get_episodes(podcast_id: str):
        with session_scope() as session:
            episodes = session.query(Episode).filter(Episode.podcast_gid == podcast_id).\
                filter(Episode.created_by == Context.get_user_id()). \
                order_by(Episode.order).all()
            return episodes

    @classmethod
    def get_episode_by_order(cls, podcast_id: str):
        with session_scope() as session:
            episode = session.query(Episode).filter(Episode.podcast_gid == podcast_id).\
                filter(Episode.created_by == Context.get_user_id()).\
                order_by(Episode.order).first()
            return episode

    @classmethod
    def get_episode_by_keys(cls, podcast_id: str, keys: List[str]):
        with session_scope() as session:
            return session.query(Episode).filter(Episode.podcast_gid == podcast_id). \
                filter(Episode.key.in_(keys)).\
                filter(Episode.created_by == Context.get_user_id()).all()

    @staticmethod
    def get_episodes_gid(podcast_id: int):
        with session_scope() as session:
            episodes = session.query(Episode).filter(Episode.podcast_gid == podcast_id).\
                filter(Episode.created_by == Context.get_user_id()).\
                order_by(Episode.order).all()
            return [episode.gid for episode in episodes]

    def get_episodes_by_podcast_gid(self, offset=0, limit=-1, order="asc"):
        with session_scope() as session:
            q = session.query(Episode).filter(Episode.podcast_gid == self.podcast_gid)
            if order == "desc":
                q = q.order_by(desc(Episode.id))
            else:
                q = q.order_by(Episode.id)

            if limit > 0:
                q = q.limit(limit).offset(offset)

            return q.all()

    def get_episodes_total_by_podcast_gid(self):
        with session_scope() as session:
            q = session.query(Episode).filter(Episode.podcast_gid == self.podcast_gid)
            return q.count()

    def get_episodes(cls, offset, limit):
        with session_scope() as session:
            episodes = session.query(Episode).order_by(desc(Episode.id)).limit(limit).offset(offset).all()
            return episodes

    def get_episodes_total(cls):
        with session_scope() as session:
            return session.query(Episode).count()

    @classmethod
    def get_episodes_without_voice(cls, podcast_gid: str):
        with session_scope() as session:
            episodes = session.query(cls).filter(cls.podcast_gid == podcast_gid).\
                filter(cls.voice_resource_id.is_(None)).all()
            return episodes

    def update(self, value):
        with session_scope() as session:
            session.query(Episode).filter(Episode.gid == self.gid).\
                filter(Episode.created_by == Context.get_user_id()).update(value)

    @staticmethod
    def batch_update(episodes, *fields):
        fields_set = set(fields)
        with session_scope() as session:
            for episode in episodes:
                fields_value = {}
                for key, value in episode.__dict__.items():
                    if key in fields_set:
                        fields_value[key] = value
                session.query(Episode).filter(Episode.gid == episode.gid).\
                    filter(Episode.created_by == Context.get_user_id()).update(fields_value)

    def get_episode_by_gid(self):
        with session_scope() as session:
            episode = session.query(Episode).filter(Episode.gid == self.gid).\
                filter(Episode.created_by == Context.get_user_id()).first()
            return episode
