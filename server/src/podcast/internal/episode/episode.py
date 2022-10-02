import io
from typing import List, Tuple

from podcast.dao.podcast import Podcast as PodcastDao, PodcastSource
from podcast.dao.episode import Episode as EpisodeDao
from podcast.pkg.segment.text_segments import TextSegment
from podcast.internal.resource.resource import Resource as ResourceInternal
from podcast.dao.base import GenStatus


class Episode:
    def __init__(self, **kwargs):
        self.gid = kwargs.get("gid")
        self.podcast_gid = kwargs.get("podcast_gid")

    def get_episode_detail(self) -> Tuple[PodcastDao, EpisodeDao]:
        episode = EpisodeDao(gid=self.gid).get_episode_by_gid()
        if episode is None:
            return None, None

        podcast = PodcastDao(gid=EpisodeDao.podcast_gid).get_by_gid()
        return podcast, episode

    def get_episodes(self, offset: int, limit: int) -> Tuple[List[EpisodeDao], int]:
        return EpisodeDao().get_episodes(offset, limit), EpisodeDao().get_episodes_total()

    def get_episode(self) -> EpisodeDao:
        return EpisodeDao(gid=self.gid).get_episode_by_gid()

    def get_episodes_by_podcast_gid(self, offset: int, limit: int = 10):
        return EpisodeDao(podcast_gid=self.podcast_gid).get_episodes_by_podcast_gid(offset, limit)

    def get_episodes_total_by_podcast_gid(self):
        return EpisodeDao(podcast_gid=self.podcast_gid).get_episodes_total_by_podcast_gid()

    @staticmethod
    def gen_language_segments(source: str, language: str, episodes: List[EpisodeDao]):
        episode_language_segments = {}
        for episode in episodes:
            if source in [PodcastSource.local, PodcastSource.rss]:
                episode_language_segments[episode.gid] = TextSegment(language, episode.content).gen_lang_segments()
            else:
                episode_language_segments[episode.gid] = episode.link
        return episode_language_segments

    def prepare_gen_episode(self):
        episode_dao = self.get_episode()
        podcast_dao: PodcastDao = PodcastDao(gid=episode_dao.podcast_gid).get_by_gid()

        return podcast_dao.gid, podcast_dao.source, Episode.gen_language_segments(podcast_dao.source, podcast_dao.language, [episode_dao])

    def update_episode(self, episode_bytes: io.BytesIO):
        object_name = "%s_%s" % (self.podcast_gid, self.gid)
        episode_size = len(episode_bytes.getbuffer())
        resource_dao = ResourceInternal(file=episode_bytes, name=f"{object_name}", type="audio").save()
        EpisodeDao(gid=self.gid).update({
            "voice_resource_id": resource_dao.gid,
            "episode_size": episode_size,
        })

    def update_gen_status(self, status: int):
        EpisodeDao(gid=self.gid).update({
            "gen_status": status,
        })