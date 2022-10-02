import unittest

import PIL
import fitz

from podcast.pkg.utils.uuid import get_uuid


class TestPDF2Image(unittest.TestCase):
    def test_get_pages(self):
        doc: fitz.Document = fitz.open("${HOME}/Desktop/高效能人士的七个习惯美.pdf")
        page: fitz.Page = doc.load_page(0)  # number of page
        pix: fitz.Pixmap = page.get_pixmap()
        output = f"/tmp/{get_uuid()}.png"
        pix.save(output)
        image = PIL.Image.open(output)
        print(image)

    def test_get_pages2(self):
        with open("${HOME}/Desktop/高效能人士的七个习惯美.pdf", "rb") as f:
            doc: fitz.Document = fitz.open(stream=f.read())
            page: fitz.Page = doc.load_page(0)  # number of page
            pix: fitz.Pixmap = page.get_pixmap()
            output = f"/tmp/{get_uuid()}.png"
            pix.save(output)
            image = PIL.Image.open(output)
            print(image)