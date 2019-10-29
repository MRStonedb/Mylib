# coding: utf-8


class BaseCache(object):
    def __init__(self, prefix):
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def _get_key(self, key):
        return "{}{}".format(self._prefix, key)
