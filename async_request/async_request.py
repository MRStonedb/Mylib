# coding: utf-8

import aiohttp
from lib.exceptions import CallServiceException


class AsyncResponse(object):
    def __init__(self, method, url):
        self._method = method
        self._url = url
        self._result = None

    @property
    def request_method(self):
        return self._method

    @property
    def request_url(self):
        return self._url

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result

    def has_exception(self):
        return isinstance(self._result, Exception)


class AsyncHttpRequest(object):
    def __init__(self, logger):
        self._logger = logger

    async def get(self, url, is_json_result=True, **kwargs):
        result = AsyncResponse(method="GET", url=url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, **kwargs) as response:
                    self._logger.debug(response)
                    response.raise_for_status()
                    result.result = (await response.text()) if not is_json_result else (await response.json())
        except aiohttp.client_exceptions.ClientError as e:
            raise CallServiceException(method="GET", url=url, errmsg=e)
        return result

    async def post(self, url, is_json_result=True, **kwargs):
        result = AsyncResponse(method="POST", url=url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, **kwargs) as response:
                    self._logger.debug(response)
                    response.raise_for_status()
                    result.result = (await response.text()) if not is_json_result else (await response.json())
        except aiohttp.client_exceptions.ClientError as e:
            raise CallServiceException(method="POST", url=url, errmsg=e)
        return result
