import datetime
import time

from bs4 import BeautifulSoup

from .podcast import Podcast, Episode
from podcast.pkg.utils.dict import get_dict_value
from podcast.pkg.utils.feed import get_rss_content_from_url
from podcast.pkg.utils.image import load_image_from_url
from urllib.parse import urlparse


class RSS:
    KIND = "RSS"

    def __init__(self, url: str, language: str):
        self.url = url

        self.language = language
        self.title = ""
        self.author = ""
        self.cover = None

        self.episodes: list[Episode] = []

    def _get_cover(self, d):
        cover = load_image_from_url(get_dict_value(d, "feed.image.href", None))
        if cover is None:
            parsed_uri = urlparse(self.url)
            favicon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(uri=parsed_uri)
            cover = load_image_from_url(favicon_url)
        return cover

    @classmethod
    def get_author(cls, d):
        author = get_dict_value(d, "feed.author_detail.name", "")

        if author == "":
            entries = d.get("entries", [])
            if len(entries) <= 0:
                return ""

            author = cls.get_author_by_entry(entries[0])
        return author

    @classmethod
    def get_author_by_entry(cls, entry):
        authors = []
        for author in entry.get('authors', []):
            name = author.get("name", "")
            if name != "":
                authors.append(name)
        return ','.join(authors)

    @classmethod
    def get_chapter_content(cls, entry):
        if hasattr(entry, 'content'):
            content = ""
            for item in entry.content:
                content += BeautifulSoup(item.value, "lxml").get_text()
            return content
        elif hasattr(entry, 'summary'):
            return BeautifulSoup(entry.summary, "lxml").get_text()
        return None

    def parse(self):
        d = get_rss_content_from_url(self.url)
        self.title = get_dict_value(d, "feed.title", "")
        self.author = self.get_author(d)
        self.cover = self._get_cover(d)

        from_index = int(round(time.time() * 1000)) * 1000 + 999

        for idx, entry in enumerate(d.get("entries")):
            title = entry.get("title", "")
            content = self.get_chapter_content(entry)
            if content is None:
                continue
            pub_time = int(time.mktime(entry.get("published_parsed")))
            self.episodes.append(Episode(from_index - idx,
                                     title,
                                     content,
                                     {"url": entry.get("link", "")},
                                     entry.get("summary", ""),
                                     None,
                                     self.get_author_by_entry(entry),
                                     entry.get("link", ""),
                                     None,
                                     entry.get("id", ""),
                                     pub_time,
                                     ))

        return Podcast(
            self.title,
            self.KIND,
            self.author,
            self.cover,
            self.language,
            "",
            self.episodes,
        )


    
