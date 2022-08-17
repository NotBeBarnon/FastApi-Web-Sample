# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 17:48
# @Author  : NotBeBarnon
# @Description : 依赖注入

from .apps import fast_app as fast_app

from .events import *
from .exceptions import *
from .middlewares import *
from .routers import *

__all__ = (
    "fast_app",
)
