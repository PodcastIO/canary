import os

from dotenv import dotenv_values


class ConfigFile:
    data = None

    @classmethod
    def load(cls):
        if cls.data is None:
            workspace = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

            cls.data = {
                **dotenv_values("{0}/conf/.env.shared".format(workspace)),  # load shared development variables
                **dotenv_values("{0}/conf/.env.secret".format(workspace)), 
                **os.environ, # override loaded values with environment variables
            }

    @classmethod
    def get_db_config(cls):
        cls.load()
        return {
            "host": cls.data.get("DB_HOST"),
            "port": int(cls.data.get("DB_PORT")),
            "user": cls.data.get("DB_USER"),
            "password": cls.data.get("DB_PASSWORD"),
            "database": cls.data.get("DB_DATABASE"),
        }

    @classmethod
    def get_minio_config(cls):
        cls.load()
        minio_port_str = cls.data.get("MINIO_PORT", "9000")
        if minio_port_str == "":
            minio_port_str = "9000"

        return {
            "host": cls.data.get("MINIO_HOST"),
            "port": int(minio_port_str),
            "access_key": cls.data.get("MINIO_ACCESS_KEY"),
            "secret_key": cls.data.get("MINIO_SECRET_KEY"),
            "episode_tmp_retention": cls.data.get("AUDIO_TMP_RETENSION", "3")
        }

    @classmethod
    def get_email_config(cls):
        cls.load()
        return {
            "smtp_host": cls.data.get("EMAIL_SMTP_SERVER"),
            "smtp_port": cls.data.get("EMAIL_SMTP_PORT"),
            "email": cls.data.get("EMAIL"),
            "password": cls.data.get("EMAIL_PASSWORD"),
            "ssl": cls.data.get("EMAIL_SSL")
        }

    @classmethod
    def get_jwt_salt(cls):
        cls.load()
        return cls.data.get("JWT_SALT")

    @classmethod
    def get_storage_address(cls):
        cls.load()
        return cls.data.get("STORAGE_ADDRESS")

    @classmethod
    def get_font_path(cls):
        workspace = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        return "{0}/conf/font.ttf".format(workspace)

    @classmethod
    def get_redis_config(cls):
        cls.load()
        return {
            "host": cls.data.get("REDIS_HOST"),
            "port": cls.data.get("REDIS_PORT"),
            "password": cls.data.get("REDIS_PASSWORD"),
        }

    @classmethod
    def get_log_config(cls):
        cls.load()
        return {
            "level": cls.data.get("LOG_LEVEL"),
            "dir": cls.data.get("LOG_DIR"),
        }

    @classmethod
    def get_podcast_share_secret_salt(cls):
        cls.load()
        return cls.data.get("PODCAST_SHARE_SECRET_SALT")
