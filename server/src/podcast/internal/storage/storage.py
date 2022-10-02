from config.conf import ConfigFile
from internal.storage.local import LocalStorage


class Storage:
    type = ConfigFile().get_storage_address()

    def __init__(self, sub_path):
        self.used_storage = None
        if type == "local":
            self.used_storage = LocalStorage(sub_path)

    def save(self, data):
        self.used_storage.save(data)

    def read(self, data):
        self.used_storage.read(data)
