import unittest

from podcast.pkg.parser.documents.text_pdf import TextPDF


class TestTextPDF(unittest.TestCase):
    def test_parse_pdf(self):
        text_pdf = TextPDF("zh")
        text_pdf.load("${HOME}/Downloads/白夜行.pdf")
        print(text_pdf.parse())

