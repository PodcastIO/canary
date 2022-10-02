import io
import logging
import os
import time
from datetime import datetime
from typing import List, Tuple
from urllib.parse import quote

import PyRSS2Gen
from starlette_context import context

from podcast.dao.podcast import Podcast as PodcastDao, PodcastSource

from podcast.dao.episode import Episode as EpisodeDao
from podcast.internal.resource.resource import Resource as InternalResource
from podcast.internal.episode.episode import Episode as EpisodeInternal
from podcast.pkg.cipher.jwt import Jwt
from podcast.pkg.errors.biz_error import PodcastShareNotSet, PodcastShareTokenInvalid
from podcast.pkg.parser.podcast import Podcast as PodcastInfo
from podcast.pkg.parser.document import Document
from podcast.pkg.parser.rss import RSS
from podcast.pkg.parser.video import Video

from podcast.pkg.type import dict_exclude_keys, str_is_empty
from podcast.pkg.segment.text_segments import TextSegment
from podcast.dao.base import GenStatus


class Podcast:
    def __init__(self, **kwargs):
        self.gid = kwargs.get("gid", "")
        self.source = kwargs.get("source", "")
        self.title = kwargs.get("title", "")
        self.author = kwargs.get("author", "")
        self.description = kwargs.get("description", "")
        self.cover_resource_id = kwargs.get("cover_resource_id", None)
        self.book_resource_id = kwargs.get("book_resource_id", None)
        self.recent_play_chapter_gid = kwargs.get("recent_play_chapter_gid", None)
        self.category_id = kwargs.get("category_id", None)
        self.language = kwargs.get("language", None)
        self.share_time = kwargs.get("share_time", None)
        self.share_enable = kwargs.get("share_enable", None)
        self.cover_url = kwargs.get("cover_url", None)
        self.url = kwargs.get("url", None)
        self.frequency = kwargs.get("frequency", None)
        self.first_execute_time = kwargs.get("first_execute_time", None)
        self.timer_id = kwargs.get("timer_id", None)

        self.blog_rss_url = kwargs.get("blog_rss_url", None)

    def __iter__(self):
        keys_map = {
            "gid": "id",
            "source": "source",
            "title": "title",
            "author": "author",
            "cover_url": "coverUrl",
            "url": "url",
            "description": "description",
            "recent_play_chapter_gid": "recentPlayChapterId",
            "language": "language",
            "share_time": "share_time",
            "share_enable": "share_enable",
            "frequency": "frequency",
            "first_execute_time": "firstExecuteTime",
            "timer_id": "timerId",
        }
        for key, new_key in keys_map.items():
            yield new_key, self.__dict__.get(key)

    def get_podcast(self) -> PodcastDao:
        podcast_dao: PodcastDao = PodcastDao(gid=self.gid)
        return podcast_dao.get_by_gid()

    def delete_podcast(self):
        podcast_dao: PodcastDao = PodcastDao(gid=self.gid)
        return podcast_dao.delete()

    def get_podcast_detail(self, offset=0, limit=100, order="desc") -> Tuple[PodcastDao, List[EpisodeDao], int]:
        podcast: PodcastDao = self.get_podcast()
        if podcast is None:
            return None, []

        episodes = EpisodeDao(podcast_gid=podcast.gid).get_episodes_by_podcast_gid( offset, limit, order)

        total = EpisodeDao(podcast_gid=podcast.gid).get_episodes_total_by_podcast_gid()
        return podcast, episodes, total

    def get_podcasts_by_gids(self, gids: List[int])->List[PodcastDao]:
        return PodcastDao.get_by_gids(gids)

    def _get_podcast_without_voice(self):
        podcast: PodcastDao = self.get_podcast()
        if podcast is None:
            return None, []
        return podcast, EpisodeDao.get_episodes_without_voice(podcast.gid)

    @classmethod
    def get_podcasts(cls, offset: int, limit: int):
        return PodcastDao.get_podcasts(offset, limit)

    @classmethod
    def get_podcasts_total(cls):
        return PodcastDao.get_podcasts_total()

    def _parse_local_book(self) -> PodcastInfo:
        resources = InternalResource.get_resources_by_gid_array([self.book_resource_id])
        book_resource_dict = resources.get(self.book_resource_id)

        document = Document(self.language)
        document.loads(book_resource_dict.get("name"), book_resource_dict.get("content"))
        return document.parse()

    def _parse_rss(self) -> PodcastInfo:
        rss = RSS(self.url, self.language)
        return rss.parse()

    def _parse_video(self) -> PodcastInfo:
        video = Video(self.language, self.url)
        return video.parse()

    def parse(self):
        podcast_dao = self.get_podcast()

        self.language = podcast_dao.language
        self.source = podcast_dao.source
        self.title = podcast_dao.title
        self.description = podcast_dao.description
        self.author = podcast_dao.author

        podcast_info: PodcastInfo = None
        if self.source == PodcastSource.local:
            self.book_resource_id = podcast_dao.book_resource_id
            podcast_info = self._parse_local_book()
        elif self.source == PodcastSource.rss:
            self.url = podcast_dao.url
            podcast_info = self._parse_rss()
        elif self.source == PodcastSource.video:
            self.url = podcast_dao.url
            podcast_info = self._parse_video()
        self.save_podcast(podcast_info)
        return podcast_info

    @classmethod
    def _gen_language_segments(cls, podcast: PodcastDao, episodes: List[EpisodeDao]):
        episode_language_segments = {}
        for episode in episodes:
            episode_language_segments[episode.gid] = TextSegment(podcast.language, episode.content).gen_lang_segments()
        return episode_language_segments

    def prepare_gen_episode(self):
        podcast_dao, episodes_dao = self._get_podcast_without_voice()
        return self.gid, podcast_dao.source, EpisodeInternal.gen_language_segments(podcast_dao.source,
                                                                               podcast_dao.language, episodes_dao)

    def add_podcast(self, name):
        if (self.title is None or self.title == "") and self.source == PodcastSource.local:
            self.title = os.path.splitext(os.path.basename(name))[0]
        podcast = PodcastDao(**dict_exclude_keys(self.__dict__, "gid"))
        podcast.save()
        return podcast

    def update_podcast_info(self, **kwargs):
        podcast = PodcastDao(gid=self.gid, **kwargs)
        podcast.update(kwargs)

    def _update_podcast(self, podcast_info: PodcastInfo):
        update_fields = {
            "title": podcast_info.title if str_is_empty(self.title) else self.title,
            "author": podcast_info.author if str_is_empty(self.author) else self.author,
            "description": podcast_info.description if str_is_empty(self.description) is None else self.description,
        }

        if podcast_info.cover is not None:
            resource_dao = InternalResource(file=podcast_info.cover, type="cover").save()
            update_fields.update({
                "cover_resource_id": resource_dao.gid
            })

        PodcastDao(gid=self.gid).update(update_fields)

    def _update_episodes(self, podcast_info: PodcastInfo):
        keys = [episode.key for episode in podcast_info.episodes]
        existed_episodes = EpisodeDao.get_episode_by_keys(self.gid, keys)
        existed_keys = set([episode.key for episode in existed_episodes])

        new_episodes = []
        for episode in podcast_info.episodes:
            if episode.key not in existed_keys:
                new_episodes.append(episode)

        episodes_dao = []
        for episode in reversed(new_episodes):
            kwargs = {
                         "podcast_gid": self.gid,
                     } | episode.__dict__

            if episode.cover is not None:
                resource_dao = InternalResource(file=episode.cover, type="cover").save()
                kwargs.update({
                    "cover_resource_id": resource_dao.gid
                })
            episodes_dao.append(EpisodeDao(**(dict_exclude_keys(kwargs, "gid"))))
        EpisodeDao.save(episodes_dao)

    def save_podcast(self, podcast_info: PodcastInfo):
        self._update_podcast(podcast_info)
        self._update_episodes(podcast_info)

        
    @classmethod
    def _gen_share_token(cls, payload: dict) -> str:
        return quote(Jwt(payload=payload).encode_share_token())

    @classmethod
    def _gen_resource_token(cls, podcast_dao: PodcastDao, resource_id: str) -> str:
        return quote(Jwt(payload={
            "podcast_id": podcast_dao.gid,
            "share_time": podcast_dao.share_time,
            "user_id": podcast_dao.created_by,
            "resource_id": resource_id,
        }).encode_share_token())

    def share_podcast(self, share_enable: bool) -> str:
        podcast_dao: PodcastDao = self.get_podcast()

        share_time = podcast_dao.share_time if podcast_dao.share_enable else int(time.time())
        if bool(podcast_dao.share_enable) != share_enable:
            podcast_dao.update({
                "share_enable": share_enable,
                "share_time": share_time,
            })

        share_token = self._gen_share_token({
            "podcast_id": podcast_dao.gid,
            "share_time": share_time,
            "user_id": podcast_dao.created_by,
        }) if share_enable else ""

        return share_token

    def gen_rss(self, share_token: str):
        podcast, episodes, _ = self.get_podcast_detail()

        if podcast.share_enable == 0:
            raise PodcastShareNotSet()

        base_url = context.data.get("base_url")
        cover_url = f"{base_url}/api/web/podcast_resource/${self._gen_resource_token(podcast, podcast.cover_resource_id)}"
        rss = PyRSS2Gen.RSS2(title=podcast.title,
                             description=podcast.title,
                             link=base_url if podcast.url is None else podcast.url,
                             image=PyRSS2Gen.Image(
                                 url=cover_url,
                                 title=podcast.title,
                                 link=cover_url,
                             ),
                             lastBuildDate=datetime.now())

        for episode in episodes:
            voice_url = f"{base_url}/api/web/podcast_resource/${self._gen_resource_token(podcast, episode.voice_resource_id)}"

            cover_resource_id = episode.cover_resource_id
            if str_is_empty(cover_resource_id):
                cover_resource_id = podcast.cover_resource_id
            episode_cover_url = f"{base_url}/api/web/podcast_resource/${self._gen_resource_token(podcast, cover_resource_id)}"
            rss.items.append(PyRSS2Gen.RSSItem(
                title=episode.title,
                link=episode.link,
                description=episode.title,
                enclosure=PyRSS2Gen.Enclosure(voice_url,
                                              episode.episode_size,
                                              "episode/mpeg"),
                guid=PyRSS2Gen.Guid(episode_cover_url, isPermaLink=1),
                pubDate=datetime.fromtimestamp(episode.pub_time if episode.pub_time else episode.created_at)
            ))

        try:
            content_io = io.BytesIO()
            rss.write_xml(content_io, "utf-8")
            return content_io
        except Exception as ex:
            logging.exception(ex)

    @staticmethod
    def check_rss_token(token: str) -> dict:
        data = Jwt(token=token).decode_share_token()
        context.data["user_id"] = data.get("user_id")
        podcast_id = data.get("podcast_id")
        share_time = data.get("share_time")

        podcast_dao = Podcast(gid=podcast_id).get_podcast()
        if not podcast_dao.share_enable:
            raise PodcastShareNotSet()

        if podcast_dao.share_time != share_time:
            raise PodcastShareTokenInvalid()
        
        return data

    def update_gen_status(self, status: int):
        podcast_dao: PodcastDao = self.get_podcast()
        podcast_dao.update({
            "gen_status": status,
        })