# coding: utf-8

import json
from functools import partial
from decimal import Decimal
from datetime import datetime, date, time
from enum import Enum
from lib.exceptions import ServerException, Error


class ResultCode(Enum):
    SUCCESS = 200
    REQUEST_FAILURE = 400
    NO_PERMISSION = 480
    INVALID_PASSWORD = 481
    INVALID_VERIFY_CODE = 482
    INVALID_TOKEN = 490
    NOT_LOGIN = 491
    DUPLICATE_LOGIN = 492
    SESSION_TIMEOUT = 493
    INVALID_ACCOUNT = 494
    FORBID_ACCOUNT = 495
    SERVER_FAILURE = 500
    DUPLICATE_DATA = 501


class HttpResult(object):
    def __init__(self, message_id=None, code=ResultCode.SUCCESS, desc=None, data=None):
        if not isinstance(code, ResultCode):
            raise ServerException(Error.INTERNAL_FAILED, "parameter code should be the instance of ResultCode")
        self._result = {"code": code.value, "desc": self._get_desc(code, desc)}
        if data is not None:
            self.data = data
        if message_id is not None:
            self.message_id = message_id

    @property
    def data(self):
        return self._result.get("data")

    @data.setter
    def data(self, data):
        self._result["data"] = data

    @property
    def message_id(self):
        return self._result.get("id")

    @message_id.setter
    def message_id(self, message_id):
        self._result["id"] = message_id

    def success(self, desc=None, data=None):
        code = ResultCode.SUCCESS
        self._result["code"] = code.value
        self._result["desc"] = self._get_desc(code, desc)
        if data is not None:
            self._result["data"] = data

    def failure(self, code, desc=None):
        if not isinstance(code, ResultCode):
            raise ServerException(Error.INTERNAL_FAILED, "parameter code should be the instance of ResultCode")
        self._result["code"] = code.value
        self._result["desc"] = self._get_desc(code, desc)

    @classmethod
    def _get_desc(cls, code, desc):
        if isinstance(desc, Exception):
            description = "{}".format(desc)
        else:
            description = desc if desc else code.name
        return description

    @property
    def result(self):
        return self._result

    @property
    def message(self):
        return json.dumps(self._result, cls=ResultJsonEncoder)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self._result)

    @staticmethod
    def is_success(result_code):
        return result_code == ResultCode.SUCCESS.value

    @staticmethod
    def is_failure(result_code):
        return result_code != ResultCode.SUCCESS.value

    @staticmethod
    def is_request_failure(result_code):
        return ResultCode.SUCCESS.value < result_code < ResultCode.SERVER_FAILURE.value

    @staticmethod
    def is_no_permission_failure(result_code):
        return result_code == ResultCode.NO_PERMISSION.value

    @staticmethod
    def is_invalid_password_failure(result_code):
        return result_code == ResultCode.INVALID_PASSWORD.value

    @staticmethod
    def is_invalid_token_failure(result_code):
        return result_code == ResultCode.INVALID_TOKEN.value

    @staticmethod
    def is_not_login_failure(result_code):
        return result_code == ResultCode.NOT_LOGIN.value

    @staticmethod
    def is_duplicate_login_failure(result_code):
        return result_code == ResultCode.DUPLICATE_LOGIN.value

    @staticmethod
    def is_session_timeout_failure(result_code):
        return result_code == ResultCode.SESSION_TIMEOUT.value

    @staticmethod
    def is_invalid_account_failure(result_code):
        return result_code == ResultCode.INVALID_ACCOUNT.value

    @staticmethod
    def is_forbid_account_failure(result_code):
        return result_code == ResultCode.FORBID_ACCOUNT.value

    @staticmethod
    def is_invalid_verify_code_failure(result_code):
        return result_code == ResultCode.INVALID_VERIFY_CODE.value

    @staticmethod
    def is_duplicate_data_failure(result_code):
        return result_code == ResultCode.DUPLICATE_DATA.value

    @staticmethod
    def is_server_failure(result_code):
        return result_code >= ResultCode.SERVER_FAILURE.value


class ResultJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, time):
            return o.strftime("%H:%M:%S")
        elif isinstance(o, Decimal):
            return float(o)
        else:
            return super(ResultJsonEncoder, self).default(o)


json_dumps = partial(json.dumps, cls=ResultJsonEncoder)
