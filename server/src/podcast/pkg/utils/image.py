import io
import ssl
import urllib.request
from PIL import Image

import podcast.pkg.client.log as logging


def get_content_from_url(url: str) -> bytes:
    if url.startswith("file:///"):
        with open(url[7:], "rb") as f:
            return f.read()
    else:
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
            req = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(req).read()
        except urllib.error.HTTPError as e:
            logging.warning("url: %s, except: %s", url, e)
            return None
        except urllib.error.URLError as e:
            logging.warning("url: %s, except: %s", url, e)
            return None


def load_image_from_url(url: str) -> Image.Image:
    if url is None or url == "":
        return None

    content = get_content_from_url(url)
    if content is None:
        return

    return Image.open(io.BytesIO(content))


