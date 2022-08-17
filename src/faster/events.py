# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 16:09
# @Author  : NotBeBarnon
# @Description : FastAPI 启动与关闭事件
import logging

from loguru import logger
from tortoise import Tortoise

from src.my_tools.logging_handler import AccessHandler, LoguruHandler
from src.settings import DATABASE_CONFIG
from .apps import fast_app

__all__ = ()


@fast_app.on_event("startup")
async def startup() -> None:
    logger.info("Startup: Message")


@fast_app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Shutdown: Message")


@fast_app.on_event("startup")
async def logger_startup() -> None:
    logging.captureWarnings(True)
    logging.root.handlers = [LoguruHandler()]

    for name in logging.root.manager.loggerDict.keys():
        logger_ = logging.getLogger(name)
        if "uvicorn" in name or "tortoise" in name:
            logger_.handlers = [AccessHandler()]
        elif "aiokafka" in name:
            logger_.handlers = []
        else:
            logger_.handlers = [LoguruHandler()]
        logger_.propagate = False


@fast_app.on_event("startup")
async def init_orm() -> None:
    await Tortoise.init(config=DATABASE_CONFIG)
    logger.success(f"Tortoise-ORM started: {Tortoise.apps}")


@fast_app.on_event("shutdown")
async def close_orm() -> None:
    await Tortoise.close_connections()
    logger.info("Tortoise-ORM shutdown")
