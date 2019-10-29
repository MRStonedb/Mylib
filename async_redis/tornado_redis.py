# coding: utf-8

from tornado import gen, concurrent
import tredis
import tredis.exceptions
from tredis.lists import ListsMixin
from tredis.client import Client, LOGGER, Command


class AsyncLists(ListsMixin):
    """
    扩展tredis的列表操作命令
    """
    def llen(self, key):
        return self._execute([b'LLEN', key])

    def lpop(self, key):
        return self._execute([b'LPOP', key])

    # noinspection PyMethodOverriding
    def rpush(self, key, value):
        return self._execute([b'RPUSH', key, value])

    def rpop(self, key):
        return self._execute([b'RPOP', key])

    # noinspection PyMethodOverriding
    def lpush(self, key, value):
        return self._execute([b'LPUSH', key, value])

    def lrange(self, key, start, stop):
        return self._execute([b'LRANGE', key, start, stop])


class TornadoRedisClient(Client, AsyncLists):
    """
    继承列表操作使tredis能够操作列表
    """
    def __init__(self, host, port, db, password=None, logger=None, io_loop=None, on_close=None, clustering=False,
                 auto_connect=True):
        super(TornadoRedisClient, self).__init__([dict(host=host, port=port, db=db)],
                                                 on_close=on_close,
                                                 io_loop=io_loop,
                                                 clustering=clustering,
                                                 auto_connect=auto_connect)
        self._reconnect_counter = 0
        self._logger = logger if logger else LOGGER

    @gen.coroutine
    def reconnect(self):
        self._logger.info("Now try to reconnect")
        yield self.connect()

    def _on_closed(self):
        self._logger.info("Connection closed")
        self._connected.clear()
        if not self._closing:
            if self._on_close_callback:
                self._on_close_callback()
            else:
                self.io_loop.spawn_callback(self.reconnect)

    def _on_connected(self, future):
        if future.exception():
            self._connect_future.set_exception(future.exception())
            self._reconnect_counter += 0 if self._reconnect_counter == 30 else 1
            self._logger.critical('Failed to connected, try reconnect after {} sec'.format(self._reconnect_counter))
            self.io_loop.call_later(self._reconnect_counter, self.reconnect)
        else:
            self._reconnect_counter = 0
            super(TornadoRedisClient, self)._on_connected(future)

    def _execute(self, parts, expectation=None, format_callback=None):
        future = concurrent.TracebackFuture()

        try:
            command = self._build_command(parts)
        except ValueError as error:
            future.set_exception(error)
            return future

        def on_locked(_):
            self._logger.debug("Lock acquired")
            if self.ready:
                if self._clustering:
                    cmd = Command(command, self._pick_cluster_host(parts), expectation, format_callback)
                else:
                    self._logger.debug('Connection: %r', self._connection)
                    cmd = Command(command, self._connection, expectation, format_callback)
                self._logger.debug('_execute(%r, %r, %r) on %s',
                                   cmd.command, expectation, format_callback, cmd.connection.name)
                cmd.connection.execute(cmd, future)
            else:
                self._logger.critical('Lock released & not ready, aborting command')
                future.set_exception(tredis.exceptions.TRedisException("Connection to redis not ready"))

        # Wait until the cluster is ready, letting cluster discovery through
        self.io_loop.add_future(self._busy.acquire(), on_locked)
        # Release the lock when the future is complete
        self.io_loop.add_future(future, lambda r: self._busy.release())
        return future
