# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 16:10
# @Author  : NotBeBarnon
# @Description : FastAPI中间件

from fastapi import Request

from .apps import fast_app

__all__ = ()


@fast_app.middleware("http")
async def middleware_func(request: Request, call_next):
    return await call_next(request)
