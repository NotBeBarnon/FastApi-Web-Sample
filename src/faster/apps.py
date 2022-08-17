# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 16:48
# @Author  : NotBeBarnon
# @Description : FastAPI的app

from fastapi import FastAPI

from src.settings import HTTP_BASE_URL, VERSION

__all__ = (
    "fast_app",
)

fast_app = FastAPI(
    title="FastSample",
    description="FastAPI 示例项目",
    version=VERSION,
    openapi_url=f"{HTTP_BASE_URL}/openapi.json",
    docs_url=f"{HTTP_BASE_URL}/docs",
    redoc_url=f"{HTTP_BASE_URL}/redoc",
    swagger_ui_oauth2_redirect_url=f"{HTTP_BASE_URL}/docs/oauth2-redirect",
)

