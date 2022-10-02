def get_dict_value(d: dict, key_path: str, default_value=None):
    keys = key_path.split(".")

    value = d
    for idx, key in enumerate(keys):
        if isinstance(value, dict):
            if idx == len(keys) - 1:
                value = value.get(key, default_value)
            else:
                value = value.get(key, {})
        else:
            return default_value
    return value


def obj_to_dict(obj):
    d = {}
    for name, value in vars(obj).items():
        if value is not None and value != "":
            d[name] = value
    return d


def model_to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}