# -*- coding: utf-8 -*-
# @Time    : 2021/12/7 9:17
# @Author  : NotBeBarnon
# @Description : 单例工具
import abc
from typing import Any

__all__ = (
    "SingletonMeta",
    "SingletonABCMeta",
)


class SingletonMeta(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]


class SingletonABCMeta(abc.ABCMeta, SingletonMeta):
    pass
