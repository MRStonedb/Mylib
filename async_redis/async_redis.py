# coding: utf-8

import asyncio
import aioredis
from lib.exceptions import ServerException, Error


class AsyncRedisClient(object):
    def __init__(self, host, port, db, password=None, logger=None, io_loop=None, minsize=1, maxsize=10):
        self._host = host
        self._port = port
        self._db = db
        self._minsize = minsize
        self._maxsize = maxsize
        self._password = password
        self._logger = logger
        self._event_loop = io_loop if io_loop else asyncio.get_event_loop()
        self._redis_client = None
        _ = asyncio.ensure_future(self.initial_client())

    def __getattr__(self, item):
        if self._redis_client is None:
            raise ServerException(errcode=Error.INTERNAL_FAILED, errmsg="Redis client not ready")
        else:
            return getattr(self._redis_client, item)

    async def initial_client(self):
        if self._redis_client is None:
            self._redis_client = await aioredis.create_redis_pool(address=(self._host, self._port),
                                                                  db=self._db,
                                                                  minsize=self._minsize,
                                                                  maxsize=self._maxsize,
                                                                  password=self._password)
            self._logger.info("now, redis is ready")
        return self._redis_client
