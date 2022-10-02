import time

from podcast.pkg.parser.documents.base_pdf import BasePDF
from podcast.pkg.parser.podcast import Podcast, Episode


class TextPDF(BasePDF):
    def __init__(self, language: str, content: bytes = b''):
        BasePDF.__init__(self, language, content)

    def parse(self) -> Podcast:
        for chapter in super().parse():
            chapter.content = self._get_chapter_text(chapter)
        self.justify_chapters()

        chapters: list[Episode] = []
        for idx, chapter in enumerate(self.chapters):
            chapters.append(Episode(
                idx,
                chapter.title,
                chapter.content,
                {},
                "",
                None,
                "",
                "",
                None,
                str(idx),
                int(time.time())
            ))

        return Podcast(
            self.title,
            self.KIND,
            self.author,
            self.cover,
            self.language,
            "",
            chapters
        )
