# -*- coding: utf-8 -*-
# @Time    : 2022/6/14 10:06
# @Author  : NotBeBarnon
# @Description :
from typing import Type

from tortoise import Model


class WriteOrReadRouter:
    def db_for_read(self, model: Type[Model]):
        return "slave"

    def db_for_write(self, model: Type[Model]):
        return "master"
