import json


class BizException(Exception):
    def __init__(self, code, msg, *args):
        self.code = code
        self.msg = self._get_msg(msg, *args)

    @classmethod
    def _get_msg(cls, base_msg: str, *args):
        msg = base_msg
        if len(args) == 1:
            msg += "({0})".format(args[0])
        elif len(args) > 1:
            msg += ("( %s )" % (args[0])).format(*args[1:])
        return msg

    def get_response(self) -> str:
        return json.dumps({
            "code": self.code,
            "msg": self.msg,
            "data": None,
        })


class SystemException(Exception):
    MSG = "system internal error"
    CODE = 10000

    def __init__(self):
        self.msg = self.MSG
        self.code = self.CODE

    def get_response(self) -> str:
        return json.dumps({
            "code": self.code,
            "msg": self.msg,
            "data": None,
        })


class CommandTimeout(BizException):
    MSG = "command timeout"
    CODE = 10001

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class PDFSyntaxError(BizException):
    MSG = "pdf syntax error"
    CODE = 10002

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class UrlNotSupport(BizException):
    MSG = "system internal error"
    CODE = 10003

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class UnknownSource(BizException):
    MSG = "unknown source"
    CODE = 10004

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class InvalidToken(BizException):
    MSG = "invalid token"
    CODE = 10005

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class InvalidGID(BizException):
    MSG = "invalid gid"
    CODE = 10006

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class SourceNotRecognize(BizException):
    MSG = "podcast source not recognize"
    CODE = 10007

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class NotUploadPodcast(BizException):
    MSG = "not upload podcast"
    CODE = 10009

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class PodcastUrlNotSet(BizException):
    MSG = "book url not set"
    CODE = 10010

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class CategoryNotSet(BizException):
    MSG = "category not set"
    CODE = 10011

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class LanguageNotInvalid(BizException):
    MSG = "language not invalid"
    CODE = 10011

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class RegisteredQueue(BizException):
    MSG = "registered queue"
    CODE = 10012

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class UnRegisteredQueue(BizException):
    MSG = "unregistered queue"
    CODE = 10012

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class BookNotExist(BizException):
    MSG = "book not exist"
    CODE = 10013

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class PodcastShareExpired(BizException):
    MSG = "podcast share expired"
    CODE = 10014

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class PodcastShareNotSet(BizException):
    MSG = "podcast not share"
    CODE = 10015

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class SchedulerFrequencyTypeInvalid(BizException):
    MSG = "scheduler frequency type not invalid"
    CODE = 10016

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class SchedulerFrequencyTypeNotSet(BizException):
    MSG = "scheduler frequency type not set"
    CODE = 10017

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class SchedulerFirstExecuteTimeNotSet(BizException):
    MSG = "scheduler first execute time not set"
    CODE = 10018

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class VideoTypeUnknown(BizException):
    MSG = "unknown video type"
    CODE = 10019

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class PodcastShareTokenInvalid(BizException):
    MSG = "podcast token invalid"
    CODE = 10020

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class ResourceInvalidType(BizException):
    MSG = "resource invalid type"
    CODE = 10021

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class EmailNotSet(BizException):
    MSG = "email not set"
    CODE = 10022

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)

class InvalidEmail(BizException):
    MSG = "email is invalid"
    CODE = 10023

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class InvalidLoginUrl(BizException):
    MSG = "invalid login url"
    CODE = 10024

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class ExpireToken(BizException):
    MSG = "token has expired."
    CODE = 10025

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class ShareDisabled(BizException):
    MSG = "share disabled"
    CODE = 10026

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class ShareExpired(BizException):
    MSG = "share expired"
    CODE = 10027

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class EmailNotExist(BizException):
    MSG = "email not exist"
    CODE = 10028

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)


class NameNotSet(BizException):
    MSG = "name not set"
    CODE = 10022

    def __init__(self, *args):
        BizException.__init__(self, self.CODE, self.MSG, *args)