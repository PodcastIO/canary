from rq_scheduler import Scheduler
from rq_scheduler.utils import setup_loghandlers

from podcast.job.podcast import parse_and_gen_podcast_job
from podcast.pkg.client.redis import redis_connection
from datetime import datetime


def launch():
    scheduler = Scheduler(queue_name=parse_and_gen_podcast_job.__name__, connection=redis_connection)
    scheduler.run(burst=False)


