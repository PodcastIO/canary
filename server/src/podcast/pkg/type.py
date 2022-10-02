import re


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def str_is_empty(s):
    return s is None or s == ''


def dict_exclude_keys(d, *exclude_keys):
    ret = {}
    exclude_keys = set(exclude_keys)
    for key, value in d.items():
        if key not in exclude_keys:
            ret[key] = value
    return ret


def check_email(email: str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    return False


def camel(s: str):
    s = re.sub(r'(_|-)+', " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])
