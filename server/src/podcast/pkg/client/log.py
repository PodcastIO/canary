import logging
import os
from logging.handlers import TimedRotatingFileHandler
from singleton_decorator import singleton

from podcast.config.conf import ConfigFile


@singleton
class PodcastLogger:
    def __init__(self):
        self._logger = self._initialize()

    def get(self) -> logging.Logger:
        return self._logger

    @classmethod
    def _get_level(cls, level: str, default: int):
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warn": logging.WARN,
            "warning": logging.WARN,
            "error": logging.ERROR,
        }
        if level.lower() in level_map:
            return level_map[level.lower()]
        return default

    @classmethod
    def _initialize(cls):
        log_conf = ConfigFile.get_log_config()

        logger = logging.getLogger(__name__)
        logger.setLevel(level=cls._get_level(log_conf.get("level"), logging.DEBUG))

        formatter = '%(asctime)s|%(filename)s|[line]:%(lineno)d|%(levelname)s|%(message)s'
        logger_dir = log_conf.get("dir", "/tmp/logger/log")
        if not os.path.exists(logger_dir):
            os.makedirs(logger_dir)

        time_rotate_handler = TimedRotatingFileHandler(filename=f"{logger_dir}/podcast_{os.environ.get('APP')}_{os.getpid()}",
                                                       when='S',
                                                       interval=2,
                                                       backupCount=5)
        time_rotate_handler.setFormatter(logging.Formatter(formatter))
        time_rotate_handler.setLevel(level=cls._get_level(log_conf.get("level"), logging.INFO))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=cls._get_level(log_conf.get("level"), logging.INFO))
        console_handler.setFormatter(logging.Formatter(formatter))

        logger.addHandler(time_rotate_handler)
        logger.addHandler(console_handler)
        return logger


def debug(msg, *args):
    PodcastLogger().get().debug(msg, *args)


def info(msg, *args):
    PodcastLogger().get().info(msg, *args)


def warning(msg, *args):
    PodcastLogger().get().warning(msg, *args)


def error(msg, *args):
    PodcastLogger().get().error(msg, *args)


def exception(msg, *args):
    PodcastLogger().get().exception(msg, *args)
