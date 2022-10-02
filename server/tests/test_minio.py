import io
import unittest

from podcast.pkg.client.minio import MinioClient


class TestMinio(unittest.TestCase):
    def test_put_file(self):
        # with open("/tmp/abc.txt", "wb") as f:
        #     f.write(b"abc")
        # with open("/tmp/abc.txt", "rb") as f:
        #     result = MinioClient("abc.txt", f).put_book()
        #     print(result)

        result = MinioClient("abc.txt").get_book()
        print(result)

    def test_get_tmp_file(self):
        # with open("/tmp/abc.txt", "wb") as f:
        #     f.write(b"abc")
        # with open("/tmp/abc.txt", "rb") as f:
        #     result = MinioClient("abc.txt", f).put_book()
        #     print(result)

        client: MinioClient = MinioClient("623dda039c11159f3f09c528_tmp_episode")
        content = client.get_tmp_episode()
        with open("/tmp/abc.mp3", "wb") as f:
            f.write(content)

    def test_put_tmp_file(self):
        # with open("/tmp/abc.txt", "wb") as f:
        #     f.write(b"abc")
        with open("${HOME}/Desktop/百年孤独.txt", "rb") as f:
            content_io = io.BytesIO(f.read())
            client: MinioClient = MinioClient("623dda039c11159f3f09c52812342_tmp_episode", content_io)
            ret = client.put_tmp_episode()
            print(ret)
