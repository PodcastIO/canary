import functools
import podcast.pkg.client.log as logging


def log_cost_time(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        import time
        begin = time.time()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
        finally:
            logging.info('func %s cost %s', func.__name__, time.time() - begin)

    return wrapped
