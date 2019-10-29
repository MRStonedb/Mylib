# coding: utf-8

import json
import asyncio
import zmq
from zmq.asyncio import Context, Poller
from lib.exceptions import DuplicateDataException, CallServiceException, ServerTimeoutException
from lib.result import HttpResult
from lib.utilities import get_unique_id
from lib.rds_bus_client.common import RdsData, RdsListData, OperationType


class AsyncRdsBusClient(object):
    """
    RDS-BUS 客户端
    """
    ASC = 1
    DESC = -1

    def __init__(self, url, logger, request_timeout=None, database=None):
        self._logger = logger
        self._database = database
        self._context = Context.instance()
        self._poller = Poller()
        self._request = self._context.socket(zmq.DEALER)
        self._request_timeout = request_timeout or 60
        self._rds_bus_url = url
        self._request.connect(self._rds_bus_url)
        self._request_dict = dict()
        self._io_loop = asyncio.get_event_loop()
        self._running = False
        asyncio.ensure_future(self.start())

    @classmethod
    def pack(cls, database: str, key: str, parameter: dict, is_query: bool = False, order_by: list = None,
             page_no: int = None, per_page: int = None, found_rows: bool = False):
        """
        打包请求数据
        :param database: RDS-BUS的数据库类名
        :param key: 数据库类所持有的实例名
        :param parameter: 参数字典
        :param is_query: 是否为查询操作
        :param order_by: 排序信息 [{"column": "字段名", "order": AsyncRdsBusClient.ASC/AsyncRdsBusClient.DESC}]
        :param page_no: 当前页（范围[0-n) n指第n页）
        :param per_page: 每页记录数
        :param found_rows: 是否统计总数
        :return:
        """
        if is_query:
            amount = int(per_page) if per_page else None
            offset = int(page_no) * amount if page_no else None
            limit = (dict(amount=amount, offset=offset) if offset else dict(amount=amount)) if amount else None
            result = dict(command="{}/{}".format(database, key),
                          data=dict(var=parameter, order_by=order_by, limit=limit, found_rows=found_rows))
        else:
            result = dict(command="{}/{}".format(database, key), data=dict(var=parameter))
        return result

    async def query(self, key: str, parameter: dict, order_by: list = None, page_no: int = None, per_page: int = None,
                    found_rows: bool = False, database: str = None, execute: bool = True):
        """
        查询接口
        :param database: RDS-BUS的数据库类名
        :param key: 数据库类所持有的语句实例名
        :param parameter: 参数字典
        :param order_by: 排序信息 [{"column": "字段名", "order": AsyncRdsBusClient.ASC/AsyncRdsBusClient.DESC}]
        :param page_no: 当前页（范围[0-n) n指第n页）
        :param per_page: 每页记录数
        :param found_rows: 是否统计总数
        :param execute: 是否执行
        :return:
        """
        _database = database or self._database
        argument = self.pack(database=_database,
                             key=key,
                             parameter=parameter,
                             is_query=True,
                             order_by=order_by,
                             page_no=page_no,
                             per_page=per_page,
                             found_rows=found_rows)
        if execute:
            response = await self._send(operation=OperationType.QUERY, argument=argument)
            result = RdsData(response)
        else:
            result = argument
        return result

    async def insert(self, key: str, parameter: dict, database: str = None, execute: bool = True):
        """
        新增接口
        :param database: RDS-BUS的数据库类名
        :param key: 数据库类所持有的语句实例名
        :param parameter: 参数字典
        :param execute: 是否执行
        :return:
        """
        _database = database or self._database
        argument = self.pack(database=_database, key=key, parameter=parameter)
        if execute:
            response = await self._send(operation=OperationType.INSERT, argument=argument)
            result = RdsData(response)
        else:
            result = argument
        return result

    async def update(self, key: str, parameter: dict, database: str=None, execute: bool = True):
        """
        更新接口
        :param database: RDS-BUS的数据库类名
        :param key: 数据库类所持有的语句实例名
        :param parameter: 参数字典
        :param execute: 是否执行
        :return:
        """
        _database = database or self._database
        argument = self.pack(database=_database, key=key, parameter=parameter)
        if execute:
            response = await self._send(operation=OperationType.UPDATE, argument=argument)
            result = RdsData(response)
        else:
            result = argument
        return result

    async def delete(self, key: str, parameter: dict, database: str = None, execute: bool = False):
        """
        删除接口
        :param database: RDS-BUS的数据库类名
        :param key: 数据库类所持有的语句实例名
        :param parameter: 参数字典
        :param execute: 是否执行
        :return:
        """
        _database = database or self._database
        argument = self.pack(database=_database, key=key, parameter=parameter)
        if execute:
            response = await self._send(operation=OperationType.DELETE, argument=argument)
            result = RdsData(response)
        else:
            result = argument
        return result

    async def transaction(self, data: list, database: str = None):
        """
        事务接口
        :param database: RDS-BUS的数据库类名
        :param data: 操作列表
        :return:
        """
        _database = database or self._database
        result = await self._send(operation=OperationType.TRANSACTION,
                                  argument=dict(command="{}/transaction".format(_database), data=data))
        return RdsListData(result)

    async def batch(self, data: list, database: str = None):
        """
        批量接口
        :param database: RDS-BUS的数据库类名
        :param data: 操作列表
        :return:
        """
        _database = database or self._database
        result = await self._send(operation=OperationType.BATCH,
                                  argument=dict(command="{}/batch".format(_database), data=data))
        return RdsListData(result)

    async def start(self):
        self._poller.register(self._request, zmq.POLLIN)
        self._running = True
        while True:
            events = await self._poller.poll()
            if self._request in dict(events):
                response = await self._request.recv_json()
                self._logger.debug("received {}".format(response))
                if response["id"] in self._request_dict:
                    future = self._request_dict.pop(response["id"])
                    if HttpResult.is_duplicate_data_failure(response["code"]):
                        future.set_exception(DuplicateDataException.new_exception(response["desc"]))
                    elif HttpResult.is_failure(response["code"]):
                        future.set_exception(CallServiceException(method="ZMQ",
                                                                  url=self._rds_bus_url,
                                                                  errmsg=response["desc"]))
                    else:
                        future.set_result(response["data"])
                else:
                    self._logger.warning("unknown response {}".format(response))

    def stop(self):
        if self._running:
            self._poller.unregister(self._request)
            self._running = False

    def shutdown(self):
        self.stop()
        self._request.close()

    def _send(self, operation, argument):
        """

        :param operation:
        :param argument:
        :return:
        """
        request_id = get_unique_id()
        self._request_dict[request_id] = asyncio.Future()
        self._io_loop.call_later(self._request_timeout, self._session_timeout, request_id)
        self._request.send_multipart([
            json.dumps(dict(id=request_id,
                            operation=operation.value,
                            argument=argument)).encode("utf-8")
        ])
        return self._request_dict[request_id]

    def _session_timeout(self, request_id):
        if request_id in self._request_dict:
            future = self._request_dict.pop(request_id)
            future.set_exception(ServerTimeoutException(method="ZMQ", url=self._rds_bus_url))
