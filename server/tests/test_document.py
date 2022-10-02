import unittest

from podcast.pkg.parser.document import Document


class TestDocument(unittest.TestCase):
    def test_parse_epub(self):
        document = Document("zh")
        document.load("${HOME}/Downloads/区块链：技术驱动金融.epub")
        print(document.parse())

    def test_parse_epub(self):
        document = Document("zh")
        document.load("${HOME}/Desktop/非暴力沟通.epub")
        print(document.parse())

    def test_en_pdf(self):
        document = Document("en")
        document.load("${HOME}/doc/animal farm.pdf")
        podcast = document.parse()
        chapters_length = {
            "Chapter I": 14035,
            "Chapter II": 14000,
            "Chapter III": 12518,
            "Chapter IV": 9723,
            "Chapter V": 17586,
            "Chapter VI": 15748,
            "Chapter VII": 20343,
            "Chapter VIII": 23006,
            "Chapter IX": 20016,
            "Chapter X": 18683,
        }
        for idx, episode in enumerate(podcast.episodes):
            episode_length = chapters_length.get(episode.title)
            self.assertEqual(len(episode.content), episode_length)

    def test_txt_pdf(self):
        document = Document("en")
        document.load("${HOME}/doc/pg1342.txt")
        podcast = document.parse()
        chapters_length = {
            "Chapter 1": 4370,
            "Chapter 2": 4189,
            "Chapter 3": 9338,
            "Chapter 4": 5822,
            "Chapter 5": 5139,
            "Chapter 6": 12728,
            "Chapter 7": 10911,
            "Chapter 8": 10740,
            "Chapter 9": 9524,
            "Chapter 10": 12190,
            "Chapter 11": 8736,
            "Chapter 12": 3863
        }
        for idx, episode in enumerate(podcast.episodes):
            length = chapters_length.get(episode.title)
            if length is not None:
                self.assertEqual(length, len(episode.content))