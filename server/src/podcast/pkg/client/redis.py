import redis

from podcast.config.conf import ConfigFile
from podcast.pkg.errors.biz_error import InvalidToken


def get_conn():
    conn = redis.Redis(host=ConfigFile.get_redis_config().get("host"),
                       port=ConfigFile.get_redis_config().get("port"),
                       password=ConfigFile.get_redis_config().get("password"))
    conn.ping()
    return conn


redis_connection = get_conn()


def _get_confirm_login_key(token):
    return "confirm_login_token_{0}".format(token)

def set_confirm_login_token(token: str, user_id: str):
    redis_connection.set(_get_confirm_login_key(token), user_id, ex=3 * 24 * 60 * 60)

def get_confirm_login_token(token: str) -> str:
    return redis_connection.get(_get_confirm_login_key(token))

def del_confirm_login_token(token: str):
    return redis_connection.delete(_get_confirm_login_key(token))

def get_confirm_login_email(cls, token):
    key: str = _get_confirm_login_key(token)
    res: bytes = redis_connection.get(key)
    redis_connection.delete(key)
    return res.decode('utf-8')

def _get_login_key(token: str):
    return "login_token_{0}".format(token)

def set_login_token(user_id: str, token: str, is_remember: bool):
    days = 1
    if is_remember:
        days = 7

    redis_connection.set(_get_login_key(token), user_id, ex=days * 24 * 60 * 60)

def get_login_token(token: str) -> str:
    key: str = _get_login_key(token)
    res: bytes = redis_connection.get(key)
    if res is None:
        raise InvalidToken()

    return res.decode('utf-8')

def delete_login_token(token: str):
    redis_connection.delete(_get_login_key(token))
