def to_str(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def zero_c():
    return b'\x0c'.decode("utf-8")


def zero_b():
    return b'\x0b'.decode("utf-8")