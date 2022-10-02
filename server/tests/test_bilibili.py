import unittest

from podcast.pkg.parser.videos.bilibili import Bilibili


class YoutubeTest(unittest.TestCase):
    def test_bilibili(self):
        bilibili = Bilibili("zh", "https://space.bilibili.com/397672/channel/collectiondetail?sid=2646")
        podcast = bilibili.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)
