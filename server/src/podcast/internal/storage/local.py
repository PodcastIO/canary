from config.conf import ConfigFile


class LocalStorage:
    directory = ConfigFile().get_storage_address()

    def __init__(self, sub_path):
        self.path = LocalStorage.directory + sub_path

    def save(self, data):
        with open(self.path, "w") as f:
            f.write(data)

    def read(self):
        with open(self.path, "r") as f:
            data = f.read()
            return data
