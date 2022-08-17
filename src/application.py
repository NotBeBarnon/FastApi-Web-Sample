# -*- coding: utf-8 -*-
# @Time    : 2021/11/24 9:37
# @Author  : NotBeBarnon
# @Description :

import typer
import uvicorn

from .settings import HTTP_API_LISTEN_HOST, HTTP_API_LISTEN_PORT

Application = typer.Typer()


@Application.command()
def run():
    uvicorn.run(
        "src.faster:fast_app",
        host=HTTP_API_LISTEN_HOST,
        port=HTTP_API_LISTEN_PORT,
        reload=False,
    )
