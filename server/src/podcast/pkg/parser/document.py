import os

from podcast.command.command import EBookConvertFile2PDFCommand, EBookConvertBuffer2PDFCommand
from .podcast import Podcast
from podcast.pkg.parser.documents.pdf import PDF


class Document:
    def __init__(self, language: str):
        self.pdf: PDF = PDF(language)

    def load(self, filepath=""):
        _, file_extension = os.path.splitext(filepath)
        if file_extension.lower() == ".pdf":
            self.pdf.load(filepath)
        else:
            output_file_path = EBookConvertFile2PDFCommand(filepath).run()
            self.pdf.load(output_file_path)

    def loads(self, filename: str, content: bytes):
        _, file_extension = os.path.splitext(filename)
        if file_extension.lower() == ".pdf":
            self.pdf.loads(filename, content)
        else:
            output_file_path = EBookConvertBuffer2PDFCommand(filename, content).run()
            self.pdf.load(output_file_path)

    def parse(self) -> Podcast:
        return self.pdf.parse()
