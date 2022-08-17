# -*- coding: utf-8 -*-
# @Time    : 2022/3/3 20:01
# @Author  : NotBeBarnon
# @Description :
import logging

from loguru import logger


class LoguruHandler(logging.Handler):
    _logger = logger

    def emit(self, record):
        try:
            level = self._logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        self._logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class AccessHandler(LoguruHandler):
    _logger = logger.bind(name="access")
