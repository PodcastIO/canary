from podcast.pkg.parser.podcast import Podcast
from podcast.pkg.parser.documents.scanner_pdf import ScannerPDF
from podcast.pkg.parser.documents.text_pdf import TextPDF


class PDF:
    def __init__(self, language: str):
        self.language = language
        self.parser = TextPDF(language)

    def load(self, filepath: str):
        self.parser.load(filepath)
        if self.parser.is_scanner():
            self.parser = ScannerPDF(self.language)
            self.parser.load(filepath)

    def loads(self, filename: str, content: bytes):
        self.parser.loads(filename, content)
        if self.parser.is_scanner():
            self.parser = ScannerPDF(self.language)
            self.parser.loads(filename, content)

    def parse(self) -> Podcast:
        return self.parser.parse()

