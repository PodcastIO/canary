import io

from podcast.pkg.errors.biz_error import VideoTypeUnknown
from podcast.pkg.mq.job import other
from podcast.pkg.parser.video import Video
from podcast.pkg.parser.videos.bilibili import Bilibili
from podcast.pkg.parser.videos.youtube import Youtube
from podcast.internal.episode.episode import Episode as EpisodeInternal
from podcast.job.job_status import start_gen_episode_context


@other('download_youtube', 10 * 600000)
def download_youtube(podcast_id: str, episode_id: str, link: str):
    with start_gen_episode_context(podcast_id, episode_id) as internal:
        with Youtube.episode(link) as video_bytes:
            EpisodeInternal(podcast_id=podcast_id, gid=episode_id).update_episode(video_bytes)


@other('download_bilibili', 10 * 600000)
def download_bilibili(podcast_id: str, episode_id: str, link: str):
    with start_gen_episode_context(podcast_id, episode_id) as internal:
        video_bytes: io.BytesIO = Bilibili.episode(link)
        EpisodeInternal(podcast_id=podcast_id, gid=episode_id).update_episode(video_bytes)


def download_video_job(podcast_id: str, episode_id: str, link: str):
    obj = Video(None, link).get_video_obj()
    if isinstance(obj, Youtube):
        return download_youtube.delay(podcast_id, episode_id, link)

    if isinstance(obj, Bilibili):
        return download_bilibili.delay(podcast_id, episode_id, link)

    raise VideoTypeUnknown()
