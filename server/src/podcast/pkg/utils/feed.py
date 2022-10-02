import io

import feedparser

from .image import get_content_from_url


def get_rss_content_from_url(url: str):
    content = get_content_from_url(url)
    feed = feedparser.parse(io.BytesIO(content))
    return feed
