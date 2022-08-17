# -*- coding: utf-8 -*-
# @Time    : 2022/4/26 17:20
# @Author  : NotBeBarnon
# @Description :
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from loguru import logger

from src.my_tools.fastapi_tools import BaseViewSet, Action
from src.settings import LOGGER_CONFIG, LOGGERS_ID
from . import app_name
from .pydantics import *

system_config_routers = APIRouter(prefix=f"/{app_name}")


class LoggerViewSet(BaseViewSet):

    @Action.get("", response_model=LoggerConfigPydantic)
    async def get_config(self):
        """
        获取日志配置
        """
        response_data = {
            name: item["level"]
            for name, item in LOGGER_CONFIG["handlers"].items()
        }
        return ORJSONResponse(response_data)

    @Action.post("", response_model=LoggerConfigPydantic)
    async def set_config(self, data: LoggerConfigPydantic):
        """修改日志配置"""
        for logger_name, level in data:
            if level is None or LOGGER_CONFIG["handlers"][logger_name]["level"] == level:
                continue

            # 1.更新配置
            LOGGER_CONFIG["handlers"][logger_name]["level"] = level.upper() if level else None
            # 2.删除旧的logger
            old_logger_id = LOGGERS_ID.pop(logger_name, None)
            if old_logger_id is not None:
                logger.warning(f"Remove logger <{logger_name}-{old_logger_id}>")
                logger.remove(old_logger_id)
            # 3.创建新的logger
            new_logger_id = logger.add(**LOGGER_CONFIG["handlers"][logger_name])
            LOGGERS_ID[logger_name] = new_logger_id
            logger.success(f"Add logger <{logger_name}-{new_logger_id}-{level}>")

        return ORJSONResponse({
            name: item["level"]
            for name, item in LOGGER_CONFIG["handlers"].items()
        })


LoggerViewSet.register(system_config_routers)
