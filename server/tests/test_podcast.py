import os
import unittest

from podcast.pkg.episode.episode import Episode
from podcast.pkg.parser.podcast import Podcast
from podcast.pkg.parser.document import Document
from podcast.run import PodCast


class PodcastTest(unittest.TestCase):
    def test_podcast1(self):
        podcast = PodCast("zh", "https://www.youtube.com/channel/UC9Q8KmHEHhDl_2LSiQNGLaQ/videos")
        podcast.run()

    def test_rss(self):
        podcast = PodCast("zh", "http://www.ruanyifeng.com/blog/atom.xml")
        podcast.run()

    def test_epub_book(self):
        document = Document("zh")
        document.load("${HOME}/Desktop/非暴力沟通.epub")
        podcast: Podcast = document.parse()
        podcast = Episode(podcast).convert()

        episode_dir = "/tmp/{0}".format(podcast.title)
        if not os.path.exists(episode_dir):
            os.mkdir(episode_dir)
        for idx, episode in enumerate(podcast.episodes):
            chapter_episode_file = "{0}/{1:03d}-{2}.mp3".format(episode_dir, idx, episode.title)
            with open(chapter_episode_file, 'wb') as out:
                out.write(episode.episode.read())
