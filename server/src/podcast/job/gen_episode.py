from contextlib import contextmanager
import io
from typing import List

from pydub import AudioSegment

from podcast.internal.episode.episode import Episode as EpisodeInternal
from podcast.job.tts import SegmentTTS
from podcast.job.video import download_video_job
from podcast.pkg.client.minio import MinioClient
from podcast.pkg.errors.biz_error import UnknownSource
from podcast.pkg.mq.job import other
from podcast.internal.podcast.podcast import Podcast as PodcastInternal
from podcast.dao.episode import Episode as EpisodeDao
from podcast.dao.podcast import Podcast as PodcastDao, PodcastSource
import podcast.pkg.client.log as logging
from podcast.internal.resource.resource import Resource as ResourceInternal

from rq import get_current_job

from podcast.dao.base import GenStatus
from podcast.job.job_status import finish_gen_episode_context, finish_gen_podcast_context


@other('finish_gen_episode_job', 10 * 60000)
def finish_gen_episode_job(podcast_id: str, episode_id: str):
    with finish_gen_episode_context(podcast_id, episode_id) as internal:
        current_job = get_current_job()
        dependency_jobs = current_job.fetch_dependencies()
        episode_meta_dicts = []
        for dependency_job in dependency_jobs:
            episode_meta_dict = dependency_job.meta[SegmentTTS.episode_meta_key]
            episode_meta_dicts.append(episode_meta_dict)
        episode_meta_dicts.sort(key=lambda x: x["idx"])

        combine_sound = None
        for episode_meta_dict in episode_meta_dicts:
            object_name = episode_meta_dict.get("object_name")
            if object_name != "":
                client = MinioClient(object_name)
                sound = AudioSegment.from_file(io.BytesIO(client.get_tmp_audio()), format="mp3")
                if combine_sound is None:
                    combine_sound = sound
                else:
                    combine_sound += sound

        if combine_sound is not None:
            combine_bytes = io.BytesIO()
            combine_sound.export(combine_bytes, format="mp3")
            internal.update_episode(combine_bytes)

@other('finish_gen_podcast_episode', 10 * 60000)
def finish_gen_podcast_episode_job(podcast_id: str):
    with finish_gen_podcast_context(podcast_id) as internal:
        pass

def gen_text_podcast(podcast_id, episode_segments):
    PodcastInternal(gid=podcast_id).update_gen_status(GenStatus.RUNNING)
    finish_episode_tasks = []
    for episode_id, episode_language_segments in episode_segments.items():
        EpisodeInternal(podcast_gid=podcast_id, gid=episode_id).update_gen_status(GenStatus.RUNNING)
        
        gen_chapter_segment_episode_tasks = []
        episode_languages, episode_segments = episode_language_segments
        for episode_segment in episode_segments:
            tts_action = SegmentTTS.get_tts_actions(episode_segment.language,
                                                    podcast_id,
                                                    episode_id,
                                                    episode_segment.idx,
                                                    episode_segment.content)
            if tts_action is not None:
                gen_chapter_segment_episode_tasks.append(tts_action())
            else:
                logging.warning("unknown language %s (%s)", episode_segment.language, episode_segment.content)

        finish_episode_tasks.append(
            finish_gen_episode_job.delay(podcast_id, episode_id, depends_on=gen_chapter_segment_episode_tasks))

    return finish_episode_tasks


def gen_video_podcast(podcast_id, episode_segments):
    finish_episode_tasks = []
    for episode_id, video_link in episode_segments.items():
        job = download_video_job(podcast_id, episode_id, video_link)
        finish_episode_tasks.append(job)
    return finish_episode_tasks


def gen_podcast(podcast_id, source, episode_segments):
    if source in [PodcastSource.local, PodcastSource.rss]:
        finish_episode_tasks = gen_text_podcast(podcast_id, episode_segments)
        finish_gen_podcast_episode_job.delay(podcast_id, depends_on=finish_episode_tasks)
        return
    if source == PodcastSource.video:
        finish_episode_tasks = gen_video_podcast(podcast_id, episode_segments)
        finish_gen_podcast_episode_job.delay(podcast_id, depends_on=finish_episode_tasks)
        return

    raise UnknownSource()


@other('gen_podcast_job', 10 * 60000)
def gen_podcast_job(podcast_id: str):
    podcast_id, source, episode_segments = PodcastInternal(gid=podcast_id).prepare_gen_episode()
    gen_podcast(podcast_id, source, episode_segments)


@other('gen_one_episode', 10 * 60000)
def gen_one_episode_job(episode_id: str):
    podcast_id, source, episode_segments = EpisodeInternal(gid=episode_id).prepare_gen_episode()
    gen_podcast(podcast_id, source, episode_segments)
