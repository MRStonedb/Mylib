# coding: utf-8

from lib.simple_cache.base_cache import BaseCache


class MemoryCache(BaseCache):
    def __init__(self, expiry, loop, prefix=""):
        super(MemoryCache, self).__init__(prefix=prefix)
        self._cache = dict()
        self._expiry = expiry
        self._loop = loop

    def get(self, key):
        self._cache.get(self._get_key(key))

    def set(self, key, value):
        real_key = self._get_key(key)
        self._cache[real_key] = value
        if self._expiry > 0:
            self._loop.call_later(self._expiry, self._timeout, real_key)

    def _timeout(self, key):
        if key in self._cache:
            self._cache.pop(key)
