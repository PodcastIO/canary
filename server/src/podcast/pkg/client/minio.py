import io
import socket

from datetime import datetime, timedelta
from minio import Minio

from minio.commonconfig import GOVERNANCE
from minio.retention import Retention

from podcast.config.conf import ConfigFile
import podcast.pkg.client.log as logging


class Buckets:
    book_bucket = "podcast-book"
    cover_bucket = "podcast-cover"
    audio_bucket = "podcast-audio"
    audio_tmp_bucket = "podcast-tmp-audio"


def _get_minio_conn():
    minio_config = ConfigFile.get_minio_config()

    conn = Minio(
        "%s:%s" % (minio_config.get("host"), minio_config.get("port")),
        access_key=minio_config.get('access_key'),
        secret_key=minio_config.get('secret_key'),
        secure=False,
    )


    for v, m in vars(Buckets).items():
        if not (v.startswith("_") or callable(m)):
            found = conn.bucket_exists(m)
            if not found:
                conn.make_bucket(m)
            else:
                logging.info("%s has already existed", m)

    return conn


_minio_connection = _get_minio_conn()


class MinioClient:
    def __init__(self, name: str, stream: io.IOBase = None):
        self._name = name
        self._stream = stream

    def put_book(self):
        self._put_content(Buckets.book_bucket, self._name, self._stream)

    def put_cover(self):
        self._put_content(Buckets.cover_bucket, self._name, self._stream)

    def put_tmp_audio(self):
        self._put_content(Buckets.audio_tmp_bucket, self._name, self._stream)

    def put_audio(self):
        self._put_content(Buckets.audio_bucket, self._name, self._stream)

    def get_book(self):
        return self._get_content(Buckets.book_bucket, self._name)

    def get_cover(self):
        return self._get_content(Buckets.cover_bucket, self._name)

    def get_tmp_audio(self):
        return self._get_content(Buckets.audio_tmp_bucket, self._name)

    def get_audio(self):
        return self._get_content(Buckets.audio_bucket, self._name)

    @classmethod
    def _put_content(cls, bucket_name: str, object_name: str, stream: io.IOBase):
        return _minio_connection.put_object(bucket_name,
                                            object_name,
                                            stream,
                                            length=-1, part_size=10 * 1024 * 1024)

    @classmethod
    def _get_content(cls, bucket_name: str, object_name: str):
        response = None
        try:
            response = _minio_connection.get_object(bucket_name, object_name)
            return response.read()
        finally:
            if response is not None:
                response.close()
                response.release_conn()
