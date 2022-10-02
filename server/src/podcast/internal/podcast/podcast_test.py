import unittest

from internal.podcast.podcast import Podcast
from internal.parser.pdf import PDFParser


class BookTest(unittest.TestCase):
    def test_parser_book(self):
        podcast = Podcast(gid="616997c463ef7fba48cba07e")
        podcast = podcast.get_book_detail()
        parser = PDFParser(podcast)
        parser.parse()
        self.assertEqual("hello", "hello")

    def test_gen_rss(self):
        podcast = Podcast(gid="6170172ca07f08b6460102b6")
        podcast.gen_rss()
        self.assertEqual("hello", "hello")

    def test_parse_rss1(self):
        podcast = Podcast(blog_rss_url="https://www.ruanyifeng.com/blog/atom.xml")
        podcast.add_rss()
        self.assertEqual("hello", "hello")

    def test_parse_rss2(self):
        podcast = Podcast(blog_rss_url="https://economist.buzzing.cc/rss.xml")
        podcast.add_rss()
        self.assertEqual("hello", "hello")
