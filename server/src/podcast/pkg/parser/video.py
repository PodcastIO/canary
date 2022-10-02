from podcast.pkg.errors.biz_error import VideoTypeUnknown
from podcast.pkg.parser.podcast import Podcast
from podcast.pkg.parser.videos.base import Base, VideoType
from podcast.pkg.parser.videos.bilibili import Bilibili
from podcast.pkg.parser.videos.youtube import Youtube


class Video:
    KIND = "Video"

    def __init__(self, language: str, url: str):
        self.language = language
        self.url = url

    def get_video_obj(self) -> Base:
        if Youtube.is_this_website(self.url):
            return Youtube(self.language, self.url)
        if Bilibili.is_this_website(self.url):
            return Bilibili(self.language, self.url)

        raise VideoTypeUnknown()

    def parse(self) -> Podcast:
        obj = self.get_video_obj()
        return obj.parse()




