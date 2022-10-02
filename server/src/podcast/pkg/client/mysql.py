from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from podcast.config.conf import ConfigFile


def _get_session():
    db_conf = ConfigFile.get_db_config()
    engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(db_conf.get("user"),
                                                                        db_conf.get("password"),
                                                                        db_conf.get("host"),
                                                                        db_conf.get("port"),
                                                                        db_conf.get("database")),
                           pool_recycle=3600,
                           echo=True,
                           encoding="utf-8")
    return sessionmaker(bind=engine)()


_session = _get_session()


@contextmanager
def session_scope():
    try:
        yield _session
        _session.flush()
        _session.commit()
    except:
        _session.rollback()
        raise


with session_scope() as s:
    s.execute('SELECT 1 + 1')
