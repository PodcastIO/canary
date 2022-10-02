import io

import PIL

from podcast.pkg.utils.dataklasses import dataklass


@dataklass
class Episode:
    order: int
    title: str
    content: str
    extra: dict
    description: str
    cover: PIL.Image
    author: str
    link: str
    episode: io.BytesIO
    key: str
    pub_time: int


@dataklass
class Podcast:
    title: str
    kind: str
    author: str
    cover: PIL.Image
    language: str
    description: str

    episodes: list[Episode]
