import binascii
import calendar
import datetime
import os
import struct
import threading
import time

from random import SystemRandom

from podcast.pkg.errors.biz_error import InvalidGID
from podcast.pkg.gid.tz_util import utc

_MAX_COUNTER_VALUE = 0xFFFFFF


def _raise_invalid_id(oid):
    raise InvalidGID(
        "%r is not a valid ObjectId, it must be a 12-byte input"
        " or a 24-character hex string" % oid)


def _random_bytes():
    """Get the 5-byte random field of an ObjectId."""
    return os.urandom(5)


class GlobalId(object):
    _pid = os.getpid()

    _inc = SystemRandom().randint(0, _MAX_COUNTER_VALUE)
    _inc_lock = threading.Lock()

    __random = _random_bytes()

    __slots__ = ('__id',)

    _type_marker = 7

    def __init__(self, oid=None):
        if oid is None:
            self.__generate()
        elif isinstance(oid, bytes) and len(oid) == 12:
            self.__id = oid
        else:
            self.__validate(oid)

    @classmethod
    def from_datetime(cls, generation_time):
        if generation_time.utcoffset() is not None:
            generation_time = generation_time - generation_time.utcoffset()
        timestamp = calendar.timegm(generation_time.timetuple())
        oid = struct.pack(
            ">I", int(timestamp)) + b"\x00\x00\x00\x00\x00\x00\x00\x00"
        return cls(oid)

    @classmethod
    def is_valid(cls, oid):
        if not oid:
            return False

        try:
            GlobalId(oid)
            return True
        except (InvalidGID, TypeError):
            return False

    @classmethod
    def _random(cls):
        """Generate a 5-byte random number once per process.
        """
        pid = os.getpid()
        if pid != cls._pid:
            cls._pid = pid
            cls.__random = _random_bytes()
        return cls.__random

    def __generate(self):
        """Generate a new value for this ObjectId.
        """

        # 4 bytes current time
        oid = struct.pack(">I", int(time.time()))

        # 5 bytes random
        oid += GlobalId._random()

        # 3 bytes inc
        with GlobalId._inc_lock:
            oid += struct.pack(">I", GlobalId._inc)[1:4]
            GlobalId._inc = (GlobalId._inc + 1) % (_MAX_COUNTER_VALUE + 1)

        self.__id = oid

    def __validate(self, oid):
        """Validate and use the given id for this ObjectId.

        Raises TypeError if id is not an instance of
        (:class:`basestring` (:class:`str` or :class:`bytes`
        in python 3), ObjectId) and InvalidId if it is not a
        valid ObjectId.

        :Parameters:
          - `oid`: a valid ObjectId
        """
        if isinstance(oid, GlobalId):
            self.__id = oid.binary
        elif isinstance(oid, str):
            if len(oid) == 24:
                try:
                    self.__id = bytes.fromhex(oid)
                except (TypeError, ValueError):
                    _raise_invalid_id(oid)
            else:
                _raise_invalid_id(oid)
        else:
            raise TypeError("id must be an instance of (bytes, str, ObjectId), "
                            "not %s" % (type(oid),))

    @property
    def binary(self):
        """12-byte binary representation of this ObjectId.
        """
        return self.__id

    @property
    def generation_time(self):
        """A :class:`datetime.datetime` instance representing the time of
        generation for this :class:`ObjectId`.

        The :class:`datetime.datetime` is timezone aware, and
        represents the generation time in UTC. It is precise to the
        second.
        """
        timestamp = struct.unpack(">I", self.__id[0:4])[0]
        return datetime.datetime.fromtimestamp(timestamp, utc)

    def __getstate__(self):
        """return value of object for pickling.
        needed explicitly because __slots__() defined.
        """
        return self.__id

    def __setstate__(self, value):
        """explicit state set from pickling
        """
        # Provide backwards compatability with OIDs
        # pickled with pymongo-1.9 or older.
        if isinstance(value, dict):
            oid = value["_ObjectId__id"]
        else:
            oid = value
        # ObjectIds pickled in python 2.x used `str` for __id.
        # In python 3.x this has to be converted to `bytes`
        # by encoding latin-1.
        if isinstance(oid, str):
            self.__id = oid.encode('latin-1')
        else:
            self.__id = oid

    def __str__(self):
        return binascii.hexlify(self.__id).decode()

    def __repr__(self):
        return "ObjectId('%s')" % (str(self),)

    def __eq__(self, other):
        if isinstance(other, GlobalId):
            return self.__id == other.binary
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, GlobalId):
            return self.__id != other.binary
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, GlobalId):
            return self.__id < other.binary
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, GlobalId):
            return self.__id <= other.binary
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, GlobalId):
            return self.__id > other.binary
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, GlobalId):
            return self.__id >= other.binary
        return NotImplemented

    def __hash__(self):
        """Get a hash value for this :class:`ObjectId`."""
        return hash(self.__id)


def get_gid():
    return str(GlobalId())