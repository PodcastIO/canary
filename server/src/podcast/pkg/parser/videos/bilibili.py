import json
import re
import time

from podcast.pkg.errors.biz_error import UrlNotSupport
from podcast.pkg.parser.videos.base import Base, VideoType
from podcast.pkg.parser.podcast import Episode, Podcast
from podcast.pkg.utils.image import get_content_from_url, load_image_from_url


class Bilibili(Base):
    KIND = VideoType.bilibili

    HOME_PAGE = "space.bilibili.com"

    def __init__(self, language, url):
        Base.__init__(self, language, url)

    def _parser_channel(self):
        search_group = re.search(r"https://space\.bilibili\.com/(\d+)/channel/collectiondetail\?sid\=(\d+)", self.url)
        if not search_group:
            raise UrlNotSupport()

        mid = search_group.group(1)
        series_id = search_group.group(2)
        return mid, series_id

    def _channel(self):
        mid, series_id = self._parser_channel()

        url = "https://api.bilibili.com/x/space/acc/info?mid={0}&jsonp=jsonp".format(mid)
        content = get_content_from_url(url)
        resp_dict: dict = json.loads(content)
        self.author = resp_dict.get("data", {}).get("name", "")
        self.cover = load_image_from_url(resp_dict.get("data", {}).get("face"))

        url = "https://api.bilibili.com/x/polymer/space/seasons_archives_list?mid={0}&season_id={1}&sort_reverse=false&page_num=1&page_size=30".format(mid, series_id)
        content = get_content_from_url(url)
        resp_dict: dict = json.loads(content)
        self.title = resp_dict.get("data", {}).get("meta", {}).get("name")

        from_index = int(round(time.time() * 1000)) * 1000 + 999
        for idx, item in enumerate(resp_dict.get("data", {}).get("archives", [])[:3]):
            episode_cover = load_image_from_url(item.get("pic"))
            self.episodes.append(Episode(
                from_index - idx,
                item.get("title"),
                "",
                {},
                "",
                episode_cover,
                "",
                "https://www.bilibili.com/video/{0}".format(item.get("bvid")),
                None,
                item.get("title"),
                int(time.time()) - idx,
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

    @classmethod
    def is_this_website(cls, url):
        return Base.is_this_website(url, cls.HOME_PAGE)

    def parse(self) -> Podcast:
        return self._channel()

