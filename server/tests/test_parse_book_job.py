import unittest
from unittest import mock

from podcast.internal.podcast.podcast import Podcast as InternalPodcast
from podcast.pkg.episode.episode import Episode
from podcast.pkg.ctx import Context
from podcast.pkg.parser.document import Document
from podcast.job.parse_podcast import parse_podcast_job


class ParsePodcastJobTest(unittest.TestCase):
    def test_parse_podcast_job(self):
        internal_podcast = InternalPodcast(gid="623746ff17a22c074e61c065").get_podcast_detail()
        podcast = Document(internal_podcast.language).parse()
        Episode(podcast).convert()

        parse_podcast_job.delay();

    def test_parse_book2(self):
        test_gid = '623d9b7ffdb7a97dfbffb737'
        Context.get_user_id = mock.Mock(return_value="123")
        internal_podcast = InternalPodcast(gid=test_gid)
        podcast = internal_podcast.parse()
        self.assertEqual(len(podcast.episodes), 1)