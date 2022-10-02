import os
import re
from abc import ABC, abstractmethod
from typing import List
import moviepy.editor as mp

from podcast.pkg.parser.podcast import Episode


class VideoType:
    youtube = 'youtube'
    bilibili = 'bilibili'


class Base(ABC):
    def __init__(self, language, url):
        self.language = language
        self.url = url

        self.title = ""
        self.author = ""
        self.cover = None

        self.episodes: List[Episode] = []

    @classmethod
    def is_this_website(cls, url, home_page):
        group = re.search(home_page, url)
        if group is not None:
            return True
        return False

    @classmethod
    def convert_to_mp3(cls, video_path):
        episode_path = "{0}.mp3".format(os.path.splitext(video_path)[0])
        my_clip = mp.VideoFileClip(video_path)
        my_clip.audio.write_audiofile(episode_path)
        return episode_path

    @abstractmethod
    def parse(self):
        pass

