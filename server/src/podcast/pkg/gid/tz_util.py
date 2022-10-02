from datetime import timedelta, tzinfo

ZERO = timedelta(0)


class FixedOffset(tzinfo):
    def __init__(self, offset, name):
        if isinstance(offset, timedelta):
            self.__offset = offset
        else:
            self.__offset = timedelta(minutes=offset)
        self.__name = name

    def __getinitargs__(self):
        return self.__offset, self.__name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


utc = FixedOffset(0, "UTC")
