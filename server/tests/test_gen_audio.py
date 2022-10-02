import logging
import unittest
from unittest import mock

from podcast.internal.podcast.podcast import Podcast as InternalBook
from podcast.dao.podcast import PodcastSource
from podcast.job.tts import SegmentTTS
from podcast.pkg.ctx import Context


class GenEpisodeTest(unittest.TestCase):
    def test_gen_episode1(self):
        Context.get_user_id = mock.Mock(return_value="123")

        book_id, source, chapters_segments = InternalBook(gid="623d9b7ffdb7a97dfbffb737").prepare_gen_episode()
        self.assertEqual(book_id, "623d9b7ffdb7a97dfbffb737")