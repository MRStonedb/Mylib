# coding: utf-8

import json as _json
import urllib.parse
import mimetypes
from functools import partial
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado import gen
from lib import CallServiceException
from lib.utils import get_unique_id


class AsyncResult(object):
    def __init__(self, response=None):
        self._response = response

    @property
    def request_method(self):
        return self._response.request.method

    @property
    def request_url(self):
        return self._response.request.url

    @property
    def request_data(self):
        return self._response.request.body

    @property
    def request_headers(self):
        return self._response.request.headers

    @property
    def response_headers(self):
        return self._response.headers

    @property
    def status_code(self):
        return self._response.code

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    @property
    def json(self):
        return _json.loads(self.text)

    @property
    def text(self):
        return self._decode_content()

    @property
    def content(self):
        return self._response.body

    def _decode_content(self):
        content = None
        if isinstance(self._response, HTTPResponse) and isinstance(self._response.body, bytes):
            content = self._response.body.decode("utf-8")
        return content

    def __str__(self):
        return '{} {} request:{} response:{}'.format(self.request_method, self.request_url, self.request_data,
                                                     self.text)
    __repr__ = __str__


class AsyncRequest(object):
    def __init__(self):
        self._client = AsyncHTTPClient()

    @gen.coroutine
    def get(self, url, params=None, **kwargs):
        """

        :param url:
        :param params:
        :param kwargs:
        :return:
        """
        method = "GET"
        if params is not None:
            kwargs.update(params)
        if kwargs:
            real_url = "{}?{}".format(url, urllib.parse.urlencode(kwargs))
        else:
            real_url = url
        try:
            result = AsyncResult()
            response = yield self._client.fetch(real_url)
            if response.error:
                raise CallServiceException(method=method, url=real_url, errmsg=response.error)
            result.response = response
        except Exception as e:
            raise CallServiceException(method=method, url=real_url, errmsg=e)
        return result

    @gen.coroutine
    def post(self, url, data=None, json=None, headers=None, use_url_encode=False, **kwargs):
        """

        :param url:
        :param data:
        :param json:
        :param headers:
        :param use_url_encode:
        :param kwargs:
        :return:
        """
        method = "POST"
        if use_url_encode:
            if headers is None:
                headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
            data = urllib.parse.urlencode(json)
        else:
            if json is not None:
                if headers is None:
                    headers = {"Content-Type": "application/json; charset=UTF-8"}
                data = _json.dumps(json)
        result = AsyncResult()
        request = HTTPRequest(url=url, method=method, body=data, headers=headers, **kwargs)
        try:
            response = yield self._client.fetch(request)
            if response.error:
                raise CallServiceException(method=method, url=url, errmsg=response.error)
            result.response = response
        except Exception as e:
            raise CallServiceException(method=method, url=url, errmsg=e)
        return result

    @gen.coroutine
    def send_file(self, url, file_names):
        """

        :param url:
        :param file_names:
        :return:
        """
        method = "POST"
        boundary = get_unique_id()
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        producer = partial(self._multipart_producer, boundary, file_names)
        result = AsyncResult()
        request = HTTPRequest(url=url, method=method, headers=headers, body_producer=producer)
        try:
            response = yield self._client.fetch(request)
            if response.error:
                raise CallServiceException(method=method, url=url, errmsg=response.error)
            result.response = response
        except Exception as e:
            raise CallServiceException(method=method, url=url, errmsg=e)
        return result

    @gen.coroutine
    def send_data_as_file(self, url, raw_data, filename=None, ext="jpg"):
        """

        :param url:
        :param filename:
        :param raw_data:
        :param ext:
        :return:
        """
        method = "POST"
        boundary = get_unique_id()
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        producer = partial(self._stream_producer, boundary, filename, ext, raw_data)
        result = AsyncResult()
        request = HTTPRequest(url=url, method=method, headers=headers, body_producer=producer)
        try:
            response = yield self._client.fetch(request)
            if response.error:
                raise CallServiceException(method=method, url=url, errmsg=response.error)
            result.response = response
        except Exception as e:
            raise CallServiceException(method=method, url=url, errmsg=e)
        return result

    @gen.coroutine
    def upload_file(self, url, raw_data, filename=None, ext="jpg"):
        """

        :param url:
        :param raw_data:
        :param filename:
        :param ext:
        :return:
        """
        method = "POST"
        boundary = get_unique_id()
        body = AsyncRequest._encode_formdata(boundary=boundary, filename=filename, ext=ext, raw_data=raw_data)
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary, 'Content-Length': len(body)}
        result = AsyncResult()
        request = HTTPRequest(url=url, method=method, headers=headers, body=body)
        try:
            response = yield self._client.fetch(request)
            if response.error:
                raise CallServiceException(method=method, url=url, errmsg=response.error)
            result.response = response
        except Exception as e:
            raise CallServiceException(method=method, url=url, errmsg=e)
        return result

    @classmethod
    @gen.coroutine
    def _multipart_producer(cls, boundary, file_names, write):
        """

        :param boundary:
        :param file_names:
        :param write:
        :return:
        """
        boundary_bytes = boundary.encode()
        for filename in file_names:
            filename_bytes = filename.encode()
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf = (
                (b'--%s\r\n' % boundary_bytes) +
                (b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' %
                 (filename_bytes, filename_bytes)) +
                (b'Content-Type: %s\r\n' % mime_type.encode()) +
                b'\r\n'
            )
            yield write(buf)
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(16 * 1024)
                    if not chunk:
                        break
                    yield write(chunk)
            yield write(b'\r\n')
        yield write(b'--%s--\r\n' % (boundary_bytes,))

    @classmethod
    @gen.coroutine
    def _stream_producer(cls, boundary, filename, ext, raw_data, write):
        """

        :param boundary:
        :param filename:
        :param ext:
        :param raw_data:
        :param write:
        :return:
        """
        boundary_bytes = boundary.encode()
        if not filename:
            filename = "{}.{}".format(boundary, ext)
        filename_bytes = filename.encode()
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        buf = (
            (b'--%s\r\n' % boundary_bytes) +
            (b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' %
             (filename_bytes, filename_bytes)) +
            (b'Content-Type: %s\r\n' % mime_type.encode()) +
            b'\r\n'
        )
        yield write(buf)
        yield write(raw_data)
        yield write(b'\r\n')
        yield write(b'--%s--\r\n' % (boundary_bytes,))

    @classmethod
    def _encode_formdata(cls, boundary, filename, ext, raw_data):
        """

        :param boundary:
        :param filename:
        :param ext:
        :param raw_data:
        :return:
        """
        crlf = b'\r\n'
        buffer = list()
        boundary_bytes = boundary.encode()
        if not filename:
            filename = "{}.{}".format(boundary, ext)
        filename_bytes = filename.encode()
        buffer.append(b'--%s' % boundary_bytes)
        buffer.append(b'Content-Disposition: form-data; name="%s"; filename="%s"' % (filename_bytes, filename_bytes))
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        buffer.append(b'Content-Type: %s' % mime_type.encode())
        buffer.append(b'')
        buffer.append(raw_data)
        buffer.append(b'--%s--' % boundary_bytes)
        buffer.append(b'')
        body = crlf.join(buffer)
        return body
