from enum import Enum
import io
import os
import re
from typing import List, Tuple

import PIL
import fitz
import pdfminer
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTImage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdf2image import convert_from_bytes

from podcast.pkg.parser.documents.chapterize import Chapterize
from podcast.pkg.utils.str import to_str
from podcast.pkg.utils.uuid import get_uuid
import podcast.pkg.client.log as logging
from fuzzysearch import find_near_matches, Match

import logging as origin_logging


origin_logging.getLogger("pdfminer.pdfinterp").setLevel(origin_logging.WARNING)


class OutlineType(Enum):
    Null = 0
    Title = 1
    Chapter = 3


class PDFChapter:
    class PDFPage:
        def __init__(self, page_no: int, page: PDFPage):
            self.page_no = page_no
            self.page = page
            self.content = ""

        def parse_text(self):
            resource_manager = PDFResourceManager()
            file_handler = io.StringIO()
            converter = TextConverter(resource_manager, file_handler, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            page_interpreter.process_page(self.page)

            self.content = str(file_handler.getvalue())
            converter.close()
            file_handler.close()
            return self.content

    def __init__(self, order, title, from_page, to_page, content: str=""):
        self.title: str = to_str(title)
        self.from_page = from_page
        self.to_page = to_page
        self.order = order
        self.content: str = ""


class BasePDF:
    KIND = "FILE"

    def __init__(self, language: str, content: bytes = b''):
        self.language = language
        self.content = io.BytesIO(content)
        self.author = ""
        self.title = ""
        self.cover = None

        self.doc = None
        self.pages: List[PDFChapter.PDFPage] = []
        self.pages_dict = {}

        self.chapters: list[PDFChapter] = []

        self.filename = "/tmp/{0}.pdf".format(get_uuid())

        self.outlines_type: OutlineType = OutlineType.Null
        self.chapter_titles: List[str] = []

        with open(self.filename, "wb") as f:
            f.write(self.content.read())

    def load(self, filepath: str = ""):
        if filepath != "":
            with open(filepath, "rb") as f:
                self.loads(filepath, f.read())

    def loads(self, filename: str, content: bytes):
        self.filename, self.content = filename, io.BytesIO(content)
        self.doc = PDFDocument(PDFParser(self.content))
        self._get_pages()

    def _get_title(self):
        title = self.doc.info[0].get("Title", "")
        try:
            self.title = to_str(title).strip()
        except UnicodeDecodeError as e:
            pass

    def _get_author(self):
        author = self.doc.info[0].get("Author")
        try:
            self.author = to_str(author).strip()
        except UnicodeDecodeError as e:
            pass

    def _get_cover(self):
        self.content.seek(0)
        doc: fitz.Document = fitz.open(stream=self.content.read())
        self.content.seek(0)
        page: fitz.Page = doc.load_page(0)  # number of page
        pix: fitz.Pixmap = page.get_pixmap()
        output = f"/tmp/{get_uuid()}.png"
        pix.save(output)
        self.cover = PIL.Image.open(output)
        os.remove(output)

    def parse(self):
        self._get_author()
        self._get_title()
        self._get_cover()

        self._get_chapter_structure()

        for chapter in self.chapters:
            logging.info("extract text from chapter [{0}]".format(chapter.title))
            yield chapter

    def _get_pages(self):
        for page_no, page in enumerate(PDFPage.create_pages(self.doc)):
            pdf_page = PDFChapter.PDFPage(page_no, page)
            self.pages_dict[page.pageid] = pdf_page
            self.pages.append(pdf_page)

    def _get_chapter_structure(self):
        try:
            outlines = self.doc.get_outlines()
        except pdfminer.pdfdocument.PDFNoOutlines as e:
            outlines = []
            self.outlines_type = OutlineType.Null

        total_pages = len(self.pages)

        order = 0
        for level, title, ref, _, _ in outlines:
            self.chapter_titles.append(title)
            self.outlines_type = OutlineType.Title
            if level != 1:
                continue
            if ref is None or len(ref) <= 0:
                continue

            page = self.pages_dict[ref[0].objid]
            if len(self.chapters) > 0:
                self.chapters[-1].to_page = page.page_no
            chapter = PDFChapter(order, title, page.page_no, total_pages)
            self.chapters.append(chapter)
            self.outlines_type = OutlineType.Chapter
            order += 1

        # no outlines
        if len(self.chapters) <= 0:
            self.chapters.append(PDFChapter(order, self.title, 0, total_pages))

    def _get_chapter_text(self, chapter):
        return self._get_pages_text(self.pages[chapter.from_page: chapter.to_page])

    def justify_chapters(self):
        if self.outlines_type == OutlineType.Title:
            self._justify_only_titles_content()
        elif self.outlines_type == OutlineType.Null:
            self._justify_none_titles_content()

        self._justify_chapters_content()

    @classmethod
    def _get_pages_text(cls, pages: list[PDFChapter.PDFPage]):
        content = ''
        for page in pages:
            content += page.parse_text()
        return content

    def is_scanner(self):
        non_searchable_pages_total = 0
        for page in self.pages:
            if 'Font' not in page.page.resources.keys():
                non_searchable_pages_total += 1

        return non_searchable_pages_total * 1.0 / len(self.pages) > 0.8

    def _justify_chapters_content(self):
        for idx, chapter in enumerate(self.chapters):
            if idx > 0:
                seg_title = re.split(' |\t|\n', chapter.title.strip())[0]
                pos = chapter.content.find(seg_title)
                if pos > 0 and chapter.content[pos + len(seg_title)].isspace():
                    self.chapters[idx - 1].content += chapter.content[:pos]
                    chapter.content = chapter.content[pos:]

        for idx, chapter in enumerate(self.chapters):
            # remove title every page
            pos = chapter.content.find(chapter.title)
            content = chapter.content[pos + len(chapter.title):]

            content = re.sub(r'(\n)(\x0b|\x0c)+%s(\n)' % chapter.title, r'\1\3',
                             content, flags=re.I)

            # remove page no
            content = re.sub(r'(\n)\d+?(\n)', r'\1\2', content, flags=re.MULTILINE | re.M)

            # solve sentence break
            content = re.sub(r'\n+(.|,|。|，)', r'\1', content, flags=re.MULTILINE | re.M)

            # solve work break
            content = re.sub(r'\n+([^.|,|。|，]+)', r'\1', content, flags=re.MULTILINE | re.M)

            # solve sentence break by new line
            content = content.strip("\x0b\x0c\n\t ")

            chapter.content = chapter.title + "\n" + content

    @classmethod
    def _select_nearest_positions(cls, matches: List[Match]) -> List[Match]:
        min_distance = 1
        for match in matches:
            if match.dist < min_distance:
                min_distance = match.dist

        nearest_matches: List[Match] = []
        for match in matches:
            if match.dist == min_distance:
                nearest_matches.append(match)
        return nearest_matches

    @classmethod
    def _select_possible_title(cls, matches: List[Match], content: str) -> List[Match]:
        possible_matches: List[Match] = []
        for match in matches:
            # match in page's begin or '\n' after match, possible is title
            if content[match.end] == '\n':
                possible_matches.append(match)
        return possible_matches

    def _reconfirm_chapters(self, titles_possible_matches: List[List[Tuple[Match, int]]]):
        class ChapterSign:
            def __init__(self):
                self.title = ""
                self.from_page = 0
                self.to_page = 0
                self.from_page_begin = 0
                self.to_page_end = 0

        invalid_titles = set()
        chapter_signs: List[ChapterSign] = []
        last_valid_title_idx = -1

        page_hits = {}
        for _, title_page_matches in enumerate(titles_possible_matches):
            for _, page_idx in title_page_matches:
                if page_idx not in page_hits:
                    page_hits[page_idx] = 0
                page_hits[page_idx] += 1

        for title_idx, title_page_matches in enumerate(titles_possible_matches):
            chapter_signs.append(ChapterSign())
            if len(title_page_matches) <= 0:
                invalid_titles.add(title_idx)
                continue

            for match, page_idx in title_page_matches:
                if (title_idx > 0 and page_idx <= chapter_signs[title_idx - 1].from_page) or page_hits[page_idx] >= 2:
                    continue
                last_valid_title_idx = title_idx
                chapter_signs[title_idx].title = self.chapter_titles[title_idx]
                chapter_signs[title_idx].from_page = page_idx
                chapter_signs[title_idx].from_page_begin = match.start
                if title_idx > 0:
                    chapter_signs[title_idx - 1].to_page = page_idx
                    chapter_signs[title_idx - 1].to_page_end = match.start
                break

        if last_valid_title_idx > 0:
            chapter_signs[last_valid_title_idx].to_page = len(self.pages) - 1
            chapter_signs[last_valid_title_idx].to_page_end = len(self.pages[-1].content)

        new_chapter_signs: List[ChapterSign] = []
        for title_idx, chapter_sign in enumerate(chapter_signs):
            if title_idx not in invalid_titles:
                new_chapter_signs.append(chapter_sign)

        new_chapters: List[PDFChapter] = []
        for new_title_idx, chapter_sign in enumerate(new_chapter_signs):
            new_chapters.append(PDFChapter(new_title_idx, chapter_sign.title, chapter_sign.from_page, chapter_sign.to_page))
            for i in range(chapter_sign.from_page, chapter_sign.to_page + 1):
                if i == chapter_sign.from_page:
                    new_chapters[-1].content += self.pages[i].content[chapter_sign.from_page_begin:]
                elif i == chapter_sign.to_page:
                    try:
                        new_chapters[-1].content += self.pages[i].content[:chapter_sign.to_page_end]
                    except:
                        print("hellworld")
                else:
                    new_chapters[-1].content += self.pages[i].content

        self.chapters = new_chapters

    def _justify_only_titles_content(self):
        title_order_matches: List[List[Tuple[Match, int]]] = []
        for title_idx, title in enumerate(self.chapter_titles):
            title_order_matches.append([])
            for page_idx, page in enumerate(self.pages):
                begin = page.content.find(f"{title}\n")
                if begin >= 0:
                    end = begin + len(f"{title}\n")
                    title_order_matches[-1].append((Match(start=begin, end=end, dist=0, matched=True), page_idx))
                # matches = find_near_matches(title, page.content, max_l_dist=1)
                # nearest_matches = self._select_nearest_positions(matches)
                # possible_matches = self._select_possible_title(nearest_matches, page.content)
                # if len(possible_matches) > 0:
                #     # title generally is the first substring in one page.
                #     title_order_matches[title_idx].append((possible_matches[0], page_idx))


        self._reconfirm_chapters(title_order_matches)

    def _justify_none_titles_content(self):
        chapters = Chapterize(self.chapters[0].content, self.language).get_text_between_headings()
        print(chapters)