# -*- coding: utf-8 -*-
# @Time    : 2022/4/26 17:20
# @Author  : NotBeBarnon
# @Description :
from enum import Enum

from pydantic import BaseModel, Field


class LoggerLevelEnum(str, Enum):
    trace = "TRACE"  # 5
    debug = "DEBUG"  # 10
    info = "INFO"
    success = "SUCCESS"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class LoggerConfigPydantic(BaseModel):
    console: LoggerLevelEnum = Field(None, description="输出到控制台的日志级别，None表示不输出到控制台")
    project: LoggerLevelEnum = Field(None, description="输出到文件的日志级别，None表示不输出到文件")
    access_console: LoggerLevelEnum = Field(None, description="输出到控制台的访问日志级别")
    access_file: LoggerLevelEnum = Field(None, description="输出到文件的访问日志级别")

    class Config:
        title = "LoggerConfigPydantic"
        schema_extra = {
            "example": {
                "console": "DEBUG",
                "project": "SUCCESS",
                "access_console": "INFO",
                "access_file": "INFO",
            }
        }
