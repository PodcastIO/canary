import io

from podcast.pkg.client.minio import MinioClient
from podcast.pkg.gid.global_id import get_gid
from podcast.pkg.mq.job import zh, en, ja, de, nl, fr, es, uk
from podcast.pkg.tts.base import BaseSpeech
from rq import get_current_job
import podcast.pkg.client.log as logging


class SegmentTTS:
    _speech: BaseSpeech = None
    use_cuda: bool = False
    language: str = ""

    episode_meta_key = "episode_detail"

    @classmethod
    def get_speech(cls):
        if cls._speech is None:
            if cls.language in ["zh", "en"]:
                from podcast.pkg.tts.paddle import PaddleSpeech
                cls._speech = PaddleSpeech(cls.language)
            else:
                from podcast.pkg.tts.coqui import CoquiSpeech
                cls._speech = CoquiSpeech(cls.language, cls.use_cuda)
        return cls._speech

    @classmethod
    def _save_tmp_episode(cls, episode_content: io.BytesIO):
        object_name = "%s_tmp_episode" % get_gid()
        client = MinioClient(object_name, episode_content)
        client.put_tmp_audio()
        return object_name

    @classmethod
    def tts(cls, podcast_id: str, episode_id: str, idx: int, content: str):
        object_name = ""
        try:
            speech: BaseSpeech = SegmentTTS.get_speech()
            for episode_content in speech.run(content):
                object_name = cls._save_tmp_episode(episode_content)
        except Exception as ex:
            logging.exception(ex)
        finally:
            job = get_current_job()
            job.meta[cls.episode_meta_key] = {
                "podcast_id": podcast_id,
                "episode_id": episode_id,
                "idx": idx,
                "object_name": object_name,
            }
            job.save_meta()

    @classmethod
    def get_tts_actions(cls, language: str, podcast_id: str, episode_id: str, content_idx: int, content: str):
        actions = {
            "zh": lambda: tts_zh.delay(podcast_id, episode_id, content_idx, content),
            "en": lambda: tts_en.delay(podcast_id, episode_id, content_idx, content),
            "ja": lambda: tts_ja.delay(podcast_id, episode_id, content_idx, content),
            "de": lambda: tts_de.delay(podcast_id, episode_id, content_idx, content),
            "nl": lambda: tts_nl.delay(podcast_id, episode_id, content_idx, content),
            "fr": lambda: tts_fr.delay(podcast_id, episode_id, content_idx, content),
            "es": lambda: tts_es.delay(podcast_id, episode_id, content_idx, content),
            "uk": lambda: tts_uk.delay(podcast_id, episode_id, content_idx, content),
        }
        return actions.get(language, None)


@zh(10 * 600000)
def tts_zh(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "zh"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@en(10 * 600000)
def tts_en(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "en"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@ja(10 * 600000)
def tts_ja(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "ja"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@de(10 * 600000)
def tts_de(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "de"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@nl(10 * 600000)
def tts_nl(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "nl"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@fr(10 * 600000)
def tts_fr(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "fr"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@es(10 * 600000)
def tts_es(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "es"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)


@uk(10 * 600000)
def tts_uk(podcast_id: str, episode_id: str, idx: int, content: str):
    SegmentTTS.language = "uk"
    SegmentTTS.tts(podcast_id, episode_id, idx, content)
