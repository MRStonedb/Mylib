# coding: utf-8

from lib.simple_cache.base_cache import BaseCache


class AsyncRedisCache(BaseCache):
    def __init__(self, client, expiry, prefix="", serializer=None, deserializer=None):
        super(AsyncRedisCache, self).__init__(prefix=prefix)
        self._client = client
        self._expiry = expiry
        self._serializer = serializer
        self._deserializer = deserializer

    async def get(self, key):
        if self._expiry > 0:
            data = await self._client.get(self._get_key(key))
            if isinstance(data, (str, bytes, bytearray)) and callable(self._deserializer):
                value = self._deserializer(data)
            else:
                value = data
        else:
            value = None
        return value

    async def set(self, key, value):
        if self._expiry > 0:
            if callable(self._serializer):
                data = self._serializer(value)
            else:
                data = value
            return await self._client.setex(self._get_key(key), self._expiry, data)
