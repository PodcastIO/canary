import io
import unittest

from podcast.pkg.parser.videos.youtube import Youtube
from podcast.pkg.type import str_is_empty
from podcast.pkg.utils.image import load_image_from_url


class YoutubeTest(unittest.TestCase):
    def test_youtube_videos(self):
        youtube = Youtube("zh", "https://www.youtube.com/channel/UC9Q8KmHEHhDl_2LSiQNGLaQ/videos")
        podcast = youtube.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)

    def test_youtube_playlist(self):
        youtube = Youtube("zh", "https://www.youtube.com/playlist?list=PLAb3N5D4yGX16OlicD-T09KpI-VLTHMpA")
        podcast = youtube.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)

    def test_youtube_videos2(self):
        youtube = Youtube("zh", "https://www.youtube.com/channel/UChgCVolsF6L7DWmOpWKSkMA/videos")
        podcast = youtube.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)

    def test_youtube_playlist3(self):
        youtube = Youtube("zh", "https://www.youtube.com/playlist?list=PL-jU8Jbi6GuW05tTyRQkWgy522AExhag5")
        podcast = youtube.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)

    def test_youtube_playlist4(self):
        youtube = Youtube("zh", "https://www.youtube.com/watch?v=02iqMAu-4pA&list=PL-jU8Jbi6GuW05tTyRQkWgy522AExhag5&index=33&ab_channel=%E8%B6%8A%E5%93%A5%E8%AF%B4%E7%94%B5%E5%BD%B1")
        podcast = youtube.parse()
        print(podcast)
        self.assertTrue(self, len(podcast.episodes) > 0)

    def test_download_youtube(self):
        with Youtube.episode("https://www.youtube.com/watch?v=DCyYp-j-xpY") as video_bytes:
            self.assertTrue(self, len(video_bytes) > 0)

    def test_image(self):
        image = load_image_from_url("https://yt3.ggpht.com/ytc/AKedOLST2bRUw6bY6Kw75uTfpjYTuCfcKmyI_z8OtStp=s88-c-k-c0x00ffffff-no-rj")

        name = image.filename
        file = io.BytesIO()
        image.save(file, format=image.format)
        if str_is_empty(name):
            name = f"cover.{image.format}"

        self.assertTrue(self, len(file.getbuffer()) > 0)
        file.seek(0)
        with open(f"/tmp/{name}", "wb") as f:
            content = file.read()
            f.write(content)

