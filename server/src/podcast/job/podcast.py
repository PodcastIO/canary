from podcast.pkg.mq.job import other
from podcast.job.parse_podcast import parse_podcast_job
from podcast.job.gen_episode import gen_podcast_job


@other('parse_and_gen_podcast_job', 10 * 600000)
def parse_and_gen_podcast_job(podcast_gid: str):
    parse_podcast_task = parse_podcast_job.delay(podcast_gid)
    gen_podcast_job.delay(podcast_gid, depends_on=[parse_podcast_task])