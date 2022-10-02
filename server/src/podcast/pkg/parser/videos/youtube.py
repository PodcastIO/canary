import io
import os
import re
import time
import uuid
from contextlib import contextmanager
from urllib import parse

from you_get import common
from you_get.common import any_download
from podcast.pkg.errors.biz_error import UrlNotSupport
from podcast.pkg.parser.videos.base import Base, VideoType
from podcast.pkg.parser.podcast import Episode, Podcast
from podcast.pkg.utils.image import load_image_from_url
from podcast.pkg.utils.playwright import open_browser_page


class Youtube(Base):
    KIND = VideoType.youtube

    HOME_PAGE = "youtube.com"

    Items = {
        "videos": {
            "title": "//ytd-channel-name[@class='style-scope ytd-c4-tabbed-header-renderer']/div/div/yt-formatted-string[@class='style-scope ytd-channel-name']",
            "cover": "//div/yt-img-shadow/img[@class='style-scope yt-img-shadow']",
            "chapter": "//ytd-grid-video-renderer[@class='style-scope ytd-grid-renderer']",
            "chapter_title": "//h3[@class='style-scope ytd-grid-video-renderer']/a[@class='yt-simple-endpoint style-scope ytd-grid-video-renderer']",
            "chapter_cover": "//div/ytd-thumbnail/a/yt-img-shadow/img[@class='style-scope yt-img-shadow']",
        },
        "playlist": {
            "title": "//h1/yt-formatted-string/a[@class='yt-simple-endpoint style-scope yt-formatted-string']",
            "cover": "//ytd-video-owner-renderer/a/yt-img-shadow/img[@class='style-scope yt-img-shadow']",
            "chapter": "//ytd-playlist-video-list-renderer/div/ytd-playlist-video-renderer/div/div[@class='style-scope ytd-playlist-video-renderer'][@id='container']",
            "chapter_title": "//div/h3/a[@class='yt-simple-endpoint style-scope ytd-playlist-video-renderer']",
            "chapter_cover": "//ytd-thumbnail/a/yt-img-shadow/img",
        }
    }

    def __init__(self, language: str, url: str):
        Base.__init__(self, language, url)

    def _get_videos(self, config: dict):
        with open_browser_page() as page:
            page.goto(self.url)

            self.title = page.query_selector(config.get("title")).inner_text()
            cover_url = page.query_selector(config.get("cover")).get_attribute("src")
            self.cover = load_image_from_url(cover_url)

            video_items = page.query_selector_all(config.get("chapter"))
            from_index = int(round(time.time() * 1000)) * 1000 + 999
            for idx, item in enumerate(video_items[:3]):
                title_selector = item.query_selector(config.get("chapter_title"))
                episode_title = title_selector.inner_text()
                episode_link = "https://{0}{1}".format(self.HOME_PAGE, title_selector.get_attribute("href"))
                episode_cover_url = item.query_selector(config.get("chapter_cover")).get_attribute("src")
                episode_cover = load_image_from_url(episode_cover_url)

                self.episodes.append(Episode(
                    from_index - idx,
                    episode_title,
                    "",
                    {},
                    "",
                    episode_cover,
                    "",
                    episode_link,
                    None,
                    episode_title,
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

    def _videos(self):
        config = self.Items.get("videos")
        return self._get_videos(config)

    def _playlist(self):
        config = self.Items.get("playlist")
        return self._get_videos(config)

    def _get_url_type(self):
        group = re.search(r"youtube.com/c(hannel)?/.*/videos", self.url)
        if group is not None:
            return self._videos

        group = re.search(r"youtube.com/playlist\?list\=.*", self.url)
        if group is not None:
            return self._playlist

        group = re.search(r"youtube.com/watch", self.url)
        if group is not None:
            params = dict(parse.parse_qsl(parse.urlsplit(self.url).query))
            self.url = "https://www.youtube.com/playlist?list={0}".format(params.get("list"))
            return self._playlist
        raise UrlNotSupport()

    @classmethod
    def is_this_website(cls, url):
        return Base.is_this_website(url, cls.HOME_PAGE)

    def parse(self) -> Podcast:
        func = self._get_url_type()
        return func()

    @classmethod
    def _download_mp4(cls, link: str):
        if not os.path.exists("/tmp/youtube"):
            os.mkdir("/tmp/youtube")

        common.output_filename = uuid.uuid4()
        any_download(link, **{
            "output_dir": "/tmp/youtube",
            "merge": True,
            "info_only": False,
            "json_output": False,
            "caption": True,
            "password": None,
            "stream_id": "18",
            "args": {
                "URL": [link],
                "auto_rename": False,
                "itag": '18',
                "timeout": 600,
                "output_dir": '/tmp/youtube',
                "output_filename": f'{common.output_filename}',
                "player": None,
                "playlist": False,
            }
        })
        return "/tmp/youtube/{0}.mp4".format(common.output_filename)

    @classmethod
    @contextmanager
    def episode(cls, link: str):
        video_path = cls._download_mp4(link)
        episode_path = cls.convert_to_mp3(video_path)
        with open(episode_path, "rb") as f:
            yield io.BytesIO(f.read())
        os.remove(video_path)
        os.remove(episode_path)



