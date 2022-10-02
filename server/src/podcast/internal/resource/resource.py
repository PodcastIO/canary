import hashlib
from inspect import classify_class_attrs
import io
import os
import uuid
from typing import List

import PIL
from PIL.Image import Image

from podcast.pkg.client.minio import MinioClient
from podcast.config.conf import ConfigFile
from podcast.dao.resource import Resource as ResourceDao
from podcast.pkg.errors.biz_error import ResourceInvalidType
from podcast.pkg.type import str_is_empty


class Resource:
    MediaTypes = {
        ".doc": "application/msword",
        ".docx": "application/msword",
        ".gif": "image/gif",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".mp3": "video/mpeg",
        ".pdf": "application/pdf",
        ".png": "image/x-png",
        ".txt": "text/plain",
        ".epub": "application/epub+zip",
    }

    def __init__(self, **kwargs):
        self._gid = kwargs.get("gid")
        self._type = kwargs.get("type")

        file = kwargs.get("file")
        if isinstance(file, Image):
            self._name = file.filename
            self._file = io.BytesIO()
            file.save(self._file, format=file.format)
            if str_is_empty(self._name):
                self._name = f"cover.{file.format}"
            self._file.seek(0)
        elif isinstance(file, io.BytesIO):
            self.file = file
            self._file = kwargs.get("file")
            self._name = kwargs.get("name")
            self._file.seek(0)
        else:
            self.file = file
            self._file = kwargs.get("file")
            self._name = kwargs.get("name")

    def _add_resource(self):
        resource_dao = ResourceDao(resource_type=self._type, name=self._name)
        resource_dao.save()
        return resource_dao

    def save(self) -> ResourceDao:
        resource_dao = self._add_resource()

        client = MinioClient("%s_%s" % (resource_dao.gid, self._name), self._file)
        put_actions = {
            "book": lambda: client.put_book(),
            "cover": lambda: client.put_cover(),
            "audio": lambda: client.put_audio(),
        }

        put_actions[self._type]()
        return resource_dao

    @classmethod
    def get_media_type(cls, name):
        _, ext = os.path.splitext(name)
        return cls.MediaTypes.get(ext, "")

    @classmethod
    def get_resources_by_gid_array(cls, gid_array):
        resources_dao: List[ResourceDao] = ResourceDao.get_by_gid_array(gid_array)

        resources_dict = {}
        for resource_dao  in resources_dao:
            minio_client = MinioClient("%s_%s" % (resource_dao.gid, resource_dao.name))

            get_actions = {
                "book": lambda: minio_client.get_book(),
                "cover": lambda: minio_client.get_cover(),
                "audio": lambda: minio_client.get_audio(),
            }

            resources_dict[resource_dao.gid] = {
                "content": get_actions[resource_dao.resource_type](),
                "media_type": cls.get_media_type(resource_dao.name),
                "name": resource_dao.name,
            }
        return resources_dict

    @classmethod
    def get_resource_detail(cls, gid: str) -> ResourceDao:
        resources_dao: ResourceDao = ResourceDao(gid=gid).get_by_gid()
        return resources_dao