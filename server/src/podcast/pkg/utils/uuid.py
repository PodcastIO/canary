import uuid

from .safe_thread import threadsafe


@threadsafe
def uuid_generator():
    """Returns a UUID4"""
    while True:
        yield str(uuid.uuid4())


def get_uuid() -> str:
    return next(uuid_generator())
