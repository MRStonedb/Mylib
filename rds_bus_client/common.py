# coding: utf-8

import math
from enum import Enum


class OperationType(Enum):
    TRANSACTION = 0
    BATCH = 1
    INSERT = 2
    UPDATE = 3
    DELETE = 4
    QUERY = 5


class RdsData(object):
    """
    RDS-BUS 结果类
    """
    def __init__(self, data, per_page=None):
        self._detail = data.get("detail")
        self._found_rows = data.get("found_rows")
        self._per_page = int(per_page) if per_page else None

    def __iter__(self):
        if isinstance(self._detail, list):
            for each_data in self._detail:
                yield each_data
        else:
            yield self._detail

    @property
    def found_rows(self):
        """
        获取查询到的记录总数
        :return:
        """
        return self._found_rows

    @property
    def total_page(self):
        """
        获取分页总页数
        :return:
        """
        return math.ceil(self._found_rows / self._per_page) if self._per_page else None

    @property
    def detail(self):
        """
        获取数据（查询结果([]/{})，插入结果({"row_id": n}),更新/删除结果({"affect_rows": n})）
        :return:
        """
        return self._detail

    def format_result(self, result_fun=None):
        """
        格式化结果（将结果进行格式化处理）
        :param result_fun: 数据处理函数 f(detail): -> data
        :return:
        """
        if callable(result_fun):
            detail = result_fun(self._detail)
        else:
            detail = self._detail
        if self._found_rows is not None:
            result = dict(detail=detail, total=self._found_rows)
        else:
            result = detail
        return result


class RdsListData(object):
    """
    RDS-BUS事务/批量处理结果类
    """
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        if isinstance(self._data, list):
            for each_data in self._data:
                yield RdsData(each_data)
        else:
            yield self._data

    def __getitem__(self, item):
        return RdsData(self._data[item])
