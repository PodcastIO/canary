import unittest

from podcast.pkg.parser.documents.scanner_pdf import ScannerPDF


class TestTextPDF(unittest.TestCase):
    def test_parse_pdf(self):
        scanner_pdf = ScannerPDF(language="zh")
        scanner_pdf.load("${HOME}/Downloads/奇点临近.pdf")
        scanner_pdf.parse()
        print(scanner_pdf.chapters)
