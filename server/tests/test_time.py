import unittest
from datetime import datetime

from podcast.dao.podcast import Podcast
from podcast.dao.episode import Episode
from podcast.dao.base import _time_now
from podcast.pkg.client.mysql import session_scope


def str_to_timestamp(t: int) -> int:
    t_str = str(t)
    year = int(t_str[:4])
    month = int(t_str[4:6])
    day = int(t_str[6:8])
    hour = int(t_str[8:10])
    minute = int(t_str[10:12])
    second = int(t_str[12:14])

    return datetime(year, month, day, hour, minute, second).timestamp()


class TestTime(unittest.TestCase):
    def test_update_create_time(self):
        with session_scope() as session:
            episodes = session.query(Episode).filter(Episode.id >= 381).all()
            for episode in episodes:
                episode.created_at = int(str_to_timestamp(episode.created_at))
                episode.updated_at = int(str_to_timestamp(episode.updated_at))
                episode.update({
                    "created_at": episode.created_at,
                    "updated_at": episode.updated_at,
                    "created_by": -1,
                    "updated_by": -1,
                })

    def test_time(self):
        print(_time_now())