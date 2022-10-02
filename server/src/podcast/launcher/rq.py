import uuid

from rq import SimpleWorker, Connection

from podcast.job.tts import SegmentTTS
from podcast.pkg.client.redis import redis_connection
from podcast.pkg.mq.job import QueuesManager


def _get_worker_name(queue_name: str) -> str:
    return f"{queue_name}_{uuid.uuid4().hex}"


def launch(queue_name: str):
    with Connection(redis_connection):
        if queue_name == 'other':
            SimpleWorker(QueuesManager.get_other_queues(), name=_get_worker_name(queue_name)).work(with_scheduler=True)
        else:
            SimpleWorker(set([queue_name]), name=_get_worker_name(f"lang_{queue_name}")).work()
            SegmentTTS.language = queue_name
            SegmentTTS.get_speech()


