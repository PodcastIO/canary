import threading


class ThreadSafeGenerator(object):
    """Wrapper around generator that protects concurrent access"""

    def __init__(self, gen):
        self.gen = gen
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.gen)


def threadsafe(f):
    """Decorator to make generator threadsafe. Fix #125"""

    def g(*a, **kw):
        return ThreadSafeGenerator(f(*a, **kw))

    return g