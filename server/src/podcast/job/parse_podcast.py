from podcast.pkg.mq.job import other
from podcast.internal.podcast.podcast import Podcast as InternalPodcast


@other('parse_podcast_job', 10 * 600000)
def parse_podcast_job(podcast_gid: str):
    InternalPodcast(gid=podcast_gid).parse()


