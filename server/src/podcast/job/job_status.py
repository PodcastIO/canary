
from contextlib import contextmanager
from podcast.internal.episode.episode import Episode as EpisodeInternal
from podcast.internal.podcast.podcast import Podcast as PodcastInternal
from podcast.dao.base import GenStatus
from podcast.dao.podcast import Podcast


@contextmanager
def finish_gen_episode_context(podcast_id: str, episode_id: str):
    internal = EpisodeInternal(podcast_gid=podcast_id, gid=episode_id)
    try:
        yield internal
        internal.update_gen_status(GenStatus.FINISH)
    except Exception as ex:
        internal.update_gen_status(GenStatus.FAILED)
        raise ex

@contextmanager
def finish_gen_podcast_context(podcast_id: str):
    internal = PodcastInternal(gid=podcast_id)
    try:
        yield internal
        internal.update_gen_status(GenStatus.FINISH)
    except Exception as ex:
        internal.update_gen_status(GenStatus.FAILED)
        raise ex

@contextmanager
def start_gen_episode_context(podcast_id: str, episode_id: str):
    podcastInternal = PodcastInternal(gid=podcast_id)
    episodeInternal = EpisodeInternal(podcast_gid=podcast_id, gid=episode_id)
    try:
        podcastInternal.update_gen_status(GenStatus.RUNNING)
        episodeInternal.update_gen_status(GenStatus.RUNNING)
        yield episodeInternal
    except Exception as ex:
        raise ex