# coding: utf-8

<<<<<<< HEAD
import re
=======
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
from enum import Enum


class Error(Enum):
    INVALID_MESSAGE = 1
    MISSING_PARAM = 2
    INVALID_PARAM = 3
    SERVER_FAILED = 4
    INTERNAL_FAILED = 5
    INVALID_COMMAND = 6
    SERVICE_FORBID = 7
<<<<<<< HEAD
    NO_PERMISSION = 8
    NOT_LOGIN = 9
    INVALID_RESOURCE = 10
    DUPLICATE_LOGIN = 11
    INVALID_ACCOUNT = 12
    INVALID_USER = 13
    INVALID_SESSION = 14
    INVALID_PASSWORD = 15
    INVALID_VERIFY_CODE = 16
    INVALID_TOKEN = 17
    FORBID_ACCOUNT = 18
    SERVER_BUSINESS = 19
    DUPLICATE_DATA = 20


class SocketException(Exception):
    """
    套接字异常类
    """
    def __init__(self, url, exception):
        self._url = url
        self._exception = exception

    def __str__(self):
        return '{} {}'.format(self._url, self._exception)
    __repr__ = __str__
=======
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625


class ApiBaseException(Exception):
    """
    异常基类
    """
    error_dict = {
<<<<<<< HEAD
        Error.INVALID_MESSAGE.value: ("Invalid message format", "错误的报文格式"),
        Error.MISSING_PARAM.value: ("Missing parameter", "缺少参数"),
        Error.INVALID_PARAM.value: ("Invalid parameter", "非法的参数"),
        Error.SERVER_FAILED.value: ("Server failed", "处理失败"),
        Error.INTERNAL_FAILED.value: ("Internal failure", "内部服务失败"),
        Error.INVALID_COMMAND.value: ("Invalid command", "无效的请求指令"),
        Error.SERVICE_FORBID.value: ("Forbid service", "非法的请求"),
        Error.NO_PERMISSION.value: ("No permission", "无权限"),
        Error.NOT_LOGIN.value: ("No login", "未登录"),
        Error.INVALID_RESOURCE.value: ("Invalid resource", "非法的请求资源"),
        Error.DUPLICATE_LOGIN.value: ("Duplicate login", "帐号已在其他地方登陆"),
        Error.INVALID_ACCOUNT.value: ("Invalid account", "账号或密码错误"),
        Error.INVALID_USER.value: ("Invalid user", "非法的用户"),
        Error.INVALID_SESSION.value: ("Invalid session", "非法的会话"),
        Error.INVALID_PASSWORD.value: ("Invalid password", "密码检验失败"),
        Error.INVALID_VERIFY_CODE.value: ("Invalid verify code", "验证码错误"),
        Error.INVALID_TOKEN.value: ("Invalid token", "登录失效"),
        Error.FORBID_ACCOUNT.value: ("Forbid account", "帐号已被禁用"),
        Error.SERVER_BUSINESS.value: ("Server is busy", "服务器忙"),
        Error.DUPLICATE_DATA.value: ("Duplicate data", "数据已存在")
    }
    description_rule = re.compile(r".*?\((?P<code>\d+)\):\s(?P<desc>.*)")
=======
        Error.INVALID_MESSAGE.value: "Invalid message format",
        Error.MISSING_PARAM.value: "Missing parameter",
        Error.INVALID_PARAM.value: "Invalid parameter",
        Error.SERVER_FAILED.value: "Request failure",
        Error.INTERNAL_FAILED.value: "Internal failure",
        Error.INVALID_COMMAND.value: "Invalid command",
        Error.SERVICE_FORBID.value: "Forbid service"
    }
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625

    def __init__(self, errcode, errmsg=None):
        """
        :param errcode: 错误代码
        :param errmsg: 错误信息
        """
        self._errmsg = errmsg
        if isinstance(errcode, Error):
            self._errcode = errcode.value
            if self._errmsg is None:
<<<<<<< HEAD
                self._errmsg = self._readable_describe
        else:
            self._errcode = errcode

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errcode=cls._translate_code(code=int(exception_data["code"])), errmsg=exception_data["desc"])
        else:
            exception = None
        return exception

    @classmethod
    def _translate_code(cls, code):
        try:
            error_code = Error(code)
        except ValueError:
            error_code = code
        return error_code

=======
                self._errmsg = self.error_dict.get(errcode.value, "Unknown")
        else:
            self._errcode = errcode

>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
    def _error_message(self):
        error_message = self._errmsg
        if isinstance(self._errmsg, Exception):
            error_message = "{}".format(self._errmsg)
        return error_message

<<<<<<< HEAD
    @property
    def _error_describe(self):
        return self.error_dict.get(self._errcode, ("Unknown", "未知的错误"))[0]

    @property
    def _readable_describe(self):
        return self.error_dict.get(self._errcode, ("Unknown", "未知的错误"))[1]

    def __str__(self):
        return '{}({}): {}'.format(self._error_describe, self._errcode, self._error_message())
=======
    def __str__(self):
        return '{}({}): {}'.format(self.error_dict.get(self._errcode, "Unknown"), self._errcode, self._error_message())
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
    __repr__ = __str__


class RequestException(ApiBaseException):
    """
    请求类异常
    """
    def __init__(self, errcode, errmsg=None):
        super(RequestException, self).__init__(errcode, errmsg)


<<<<<<< HEAD
class InvalidAccountException(RequestException):
    """
    非法账户异常
    """
    def __init__(self, errmsg=None):
        super(InvalidAccountException, self).__init__(Error.INVALID_ACCOUNT, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class ForbidAccountException(RequestException):
    """
    帐号禁用异常
    """
    def __init__(self, errmsg=None):
        super(ForbidAccountException, self).__init__(Error.FORBID_ACCOUNT, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidUserException(RequestException):
    """
    非法用户异常
    """
    def __init__(self, errmsg=None):
        super(InvalidUserException, self).__init__(Error.INVALID_USER, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidUserStateException(RequestException):
    """
    用户状态异常
    """
    def __init__(self, errmsg=None):
        super(InvalidUserStateException, self).__init__(Error.NOT_LOGIN, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class DuplicateLogin(RequestException):
    """
    重复登录异常
    """
    def __init__(self, errmsg=None):
        super(DuplicateLogin, self).__init__(Error.DUPLICATE_LOGIN, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class NoPermissionException(RequestException):
    """
    无权限异常
    """
    def __init__(self, errmsg=None):
        super(NoPermissionException, self).__init__(Error.NO_PERMISSION, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidSessionException(RequestException):
    """
    非法的会话异常
    """
    def __init__(self, errmsg=None):
        super(InvalidSessionException, self).__init__(Error.INVALID_SESSION, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidPasswordException(RequestException):
    """
    非法的密码
    """
    def __init__(self, errmsg=None):
        super(InvalidPasswordException, self).__init__(Error.INVALID_PASSWORD, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidVerifyCodeException(RequestException):
    """
    非法的验证码
    """
    def __init__(self, errmsg=None):
        super(InvalidVerifyCodeException, self).__init__(Error.INVALID_VERIFY_CODE, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class InvalidTokenException(RequestException):
    """
    非法的TOKEN
    """
    def __init__(self, errmsg=None):
        super(InvalidTokenException, self).__init__(Error.INVALID_TOKEN, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


=======
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
class ServerException(ApiBaseException):
    """
    服务类异常
    """
    def __init__(self, errcode, errmsg=None):
        super(ServerException, self).__init__(errcode, errmsg)


<<<<<<< HEAD
class InvalidStatement(ServerException):
    """
    无效的语句
    """
    def __init__(self, errmsg=None):
        super(InvalidStatement, self).__init__(errcode=Error.INTERNAL_FAILED, errmsg=errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


class DuplicateDataException(ServerException):
    """
    重复数据异常
    """
    def __init__(self, errmsg=None):
        super(DuplicateDataException, self).__init__(Error.DUPLICATE_DATA, errmsg)

    @classmethod
    def new_exception(cls, description):
        matcher = cls.description_rule.match(description)
        if matcher is not None:
            exception_data = matcher.groupdict()
            exception = cls(errmsg=exception_data["desc"])
        else:
            exception = None
        return exception


=======
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
class CallServiceException(ServerException):
    """
    调用远端服务异常
    """
<<<<<<< HEAD
    def __init__(self, method, url, errcode=Error.SERVER_FAILED, errmsg=None):
        super(CallServiceException, self).__init__(errcode, errmsg)
=======
    def __init__(self, method, url, errmsg=None):
        super(CallServiceException, self).__init__(Error.SERVER_FAILED, errmsg)
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
        self._call_method = method
        self._service_url = url

    @property
    def service_url(self):
        return self._service_url

    def _error_message(self):
<<<<<<< HEAD
        return "{} {} failed, desc({})".format(
            self._call_method, self._service_url, super(CallServiceException, self)._error_message())


class ServerTimeoutException(CallServiceException):
    """
    服务端超时异常
    """
    def __init__(self, method, url):
        super(ServerTimeoutException, self).__init__(method=method, url=url, errcode=Error.SERVER_BUSINESS)

    def _error_message(self):
        return "{} {} failed, desc({})".format(self._call_method, self.service_url, self._readable_describe)
=======
        return '{} {} failed, desc({})'.format(
            self._call_method, self._service_url, super(CallServiceException, self)._error_message())
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
