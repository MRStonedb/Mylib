# coding: utf-8

import math
import pyDes


class DesCrypto(object):
    def __init__(self, key):
        self._des = pyDes.des(key, pyDes.ECB)

    def encode(self, src):
        if not isinstance(src, bytes):
            parameter = str(src).encode("utf-8")
        else:
            parameter = src
        reserve = math.ceil(len(parameter) / 8) * 8 - len(parameter)  # 计算补位数量
        param = parameter + (chr(reserve) * reserve).encode("utf-8")  # 补足位数（必须为8的倍数）
        result = self._des.encrypt(param)
        return result

    def decode(self, src):
        if isinstance(src, str):
            parameter = bytes([int(src[i:i+2], base=16) for i in range(0, len(src), 2)])
        else:
            parameter = src
        result = self._des.decrypt(parameter)
        return result[:-result[-1]] if result[-1] < 8 else result
