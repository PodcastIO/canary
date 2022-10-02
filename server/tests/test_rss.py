import unittest

from podcast.pkg.parser.rss import RSS


class TestRSS(unittest.TestCase):
    def test_parse_text_blog(self):
        rss = RSS("http://www.ruanyifeng.com/blog/atom.xml", "zh")
        rss.parse()
        print(rss.episodes)

    def test_parse_bilibili(self):
        rss = RSS("https://www.ximalaya.com/podcast/8867744.xml", "zh")
        ablum = rss.parse()
        print(ablum.episodes)

    def test_parse_linuxcn(self):
        rss = RSS("https://linux.cn/rss.xml", "zh")
        ablum = rss.parse()
        print(ablum)

    def test_parse_36kr(self):
        rss = RSS("https://36kr.com/feed", "zh")
        ablum = rss.parse()
        print(ablum)

    def test_parse_wanqu(self):
        rss = RSS("https://wanqu.co/feed/", "zh")
        ablum = rss.parse()
        print(ablum)