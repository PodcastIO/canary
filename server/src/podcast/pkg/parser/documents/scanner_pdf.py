import ocrmypdf

from podcast.pkg.parser.documents.base_pdf import BasePDF


import logging as origin_logging
origin_logging.getLogger("img2pdf").setLevel(origin_logging.INFO)
origin_logging.getLogger("ocrmypdf._pipeline").setLevel(origin_logging.INFO)
origin_logging.getLogger("PIL.PngImagePlugin").setLevel(origin_logging.INFO)
origin_logging.getLogger("ocrmypdf.subprocess").setLevel(origin_logging.INFO)
origin_logging.getLogger("ocrmypdf._pipeline").setLevel(origin_logging.INFO)


class ScannerPDF(BasePDF):
    def __init__(self, language: str):
        BasePDF.__init__(self, language=language)

    def load(self, filepath: str):
        ocrmypdf_language = self.language
        if self.language == "zh":
            ocrmypdf_language = "eng+chi_sim"
        ocrmypdf.ocr(filepath, self.filename, language=ocrmypdf_language, deskew=True)

        super().load(self.filename)

    def parse(self):
        for chapter in super().parse():
            chapter.content = self._get_chapter_text(chapter)
