import unittest

import ocrmypdf


class TextOCRMyPDF(unittest.TestCase):
    def test_ocrmypdf(self):
        ocrmypdf.ocr('${HOME}/Downloads/奇点临近.pdf', '/tmp/output.pdf', language="eng+chi_sim", deskew=True)
