# -*- coding: utf-8 -*-
# @Time    : 2022/5/10 20:01
# @Author  : NotBeBarnon
# @Description :
import asyncio
from typing import Tuple, Union, Dict

import aiohttp
from aiohttp import ClientConnectionError
from loguru import logger


class BaseHTTPClient(object):
    __client_session: Dict[str, aiohttp.ClientSession] = {}
    __base_url: Dict[str, str] = {}

    def __init__(self):
        super().__init__()

    @staticmethod
    async def client_session_request(method, url, **kwargs) -> Tuple[int, Union[bytes, str]]:
        code_, bytes_data_ = 500, b""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as resp:
                    code_ = resp.status
                    bytes_data_ = await resp.read()
        except ClientConnectionError as exc:
            bytes_data_ = f"{exc.__class__.__name__}:{exc}"
        except asyncio.TimeoutError as exc:
            code_ = 600
            bytes_data_ = f"{url} asyncio TimeoutError"
        except Exception as exc:
            logger.exception(f"{url} - {exc.__class__.__name__}:{exc}")
            bytes_data_ = f"{url} - {exc.__class__.__name__}:{exc}"

        return code_, bytes_data_

    async def request(self, method, url, **kwargs) -> Tuple[int, Union[bytes, str]]:
        """
        发送请求
        Args:
            method: 请求类型
            url:  url
        """
        code_, bytes_data_ = 500, b""
        try:
            async with self.get_client().request(method, url, **kwargs) as resp:
                code_ = resp.status
                bytes_data_ = await resp.read()
        except ClientConnectionError as exc:
            bytes_data_ = f"{url} - {exc.__class__.__name__}:{exc}"
        except asyncio.TimeoutError as exc:
            code_ = 600
            bytes_data_ = f"{url} asyncio TimeoutError"
        except Exception as exc:
            logger.exception(f"{url} - {exc.__class__.__name__}:{exc}")
            bytes_data_ = f"{url} - {exc.__class__.__name__}:{exc}"

        return code_, bytes_data_

    async def get(self, url, **kwargs) -> Tuple[int, Union[bytes, str]]:
        return await self.request("GET", url, **kwargs)

    async def post(self, url, **kwargs) -> Tuple[int, Union[bytes, str]]:
        return await self.request("POST", url, **kwargs)

    async def patch(self, url, **kwargs) -> Tuple[int, Union[bytes, str]]:
        return await self.request("PATCH", url, **kwargs)

    @classmethod
    def set_base_url(cls, base_url: str):
        cls.__base_url[cls.__name__] = base_url

    @classmethod
    def set_client(cls, client: aiohttp.ClientSession):
        if isinstance(client, aiohttp.ClientSession):
            cls.__client_session[cls.__name__] = client
            return True
        return False

    @classmethod
    def get_client(cls):
        client_ = cls.__client_session.get(cls.__name__, None)
        if not (isinstance(client_, aiohttp.ClientSession) and not client_.closed):
            client_ = aiohttp.ClientSession(cls.__base_url.get(cls.__name__, None))
            cls.__client_session[cls.__name__] = client_

        return client_

    @classmethod
    async def close(cls):
        for client_ in cls.__client_session.values():
            if isinstance(client_, aiohttp.ClientSession):
                await client_.close()
