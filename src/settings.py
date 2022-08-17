# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 16:51
# @Author  : NotBeBarnon
# @Description : 配置文件
import datetime
import json
import os
import sys
from pathlib import Path

import dotenv
import tomlkit
from loguru import logger as __logger

# 项目根目录
PROJECT_DIR: Path = Path(__file__).parents[1]
if PROJECT_DIR.name == "lib":  # 适配cx_Freeze打包项目后根目录的变化
    PROJECT_DIR = PROJECT_DIR.parent

# 加载环境变量
dotenv.load_dotenv(PROJECT_DIR.joinpath("project_env"))
# 加载项目配置
__toml_config = json.loads(
    json.dumps(
        tomlkit.loads(PROJECT_DIR.joinpath("pyproject.toml").read_bytes())
    )
)  # 转换包装类型为Python默认类型

VERSION = __toml_config["tool"]["commitizen"]["version"]
VERSION_FORMAT = __toml_config["tool"]["commitizen"]["tag_format"].replace("$version", VERSION)
PROJECT_CONFIG = __toml_config["myproject"]

# DEBUG控制
DEV = PROJECT_CONFIG.get("dev", False)
# 生产环境控制
PROD = not DEV and PROJECT_CONFIG.get("prod", True)

DEV and __logger.info(f"[DEV] Server - Version:{VERSION_FORMAT}")
PROD and __logger.info(f"[PROD] Server - Version:{VERSION_FORMAT}")

# 服务监听
HTTP_API_LISTEN_HOST = PROJECT_CONFIG.get("http_api_listen_host", "0.0.0.0")
HTTP_API_LISTEN_PORT = int(os.getenv("HTTP_API_LISTEN_PORT", PROJECT_CONFIG.get("http_api_listen_port", 8080)))
HTTP_BASE_URL = PROJECT_CONFIG.get("http_base_url", "/api/sample")

# 配置日志
LOG_LEVEL = PROJECT_CONFIG["log"]["level"].upper()
LOGGER_CONFIG = {
    "handlers": {
        "console": {
            "sink": sys.stdout,
            "level": LOG_LEVEL,
            "enqueue": True,
            "backtrace": False,
            "diagnose": True,
            "catch": True,
            "filter": lambda record: "name" not in record["extra"],
        },
        "project": {
            "sink": PROJECT_DIR.joinpath(PROJECT_CONFIG["log"]["file_path"], "project.log"),
            "rotation": "3 MB",
            "retention": datetime.timedelta(hours=float(PROJECT_CONFIG["log"].get("retention", 168))),
            "level": PROJECT_CONFIG["log"]["file_level"].upper(),
            "enqueue": True,
            "backtrace": False,
            "diagnose": True,
            "encoding": "utf-8",
            "catch": True,
            "filter": lambda record: "name" not in record["extra"],
        },
        "access_console": {
            "sink": sys.stdout,
            "level": PROJECT_CONFIG["log"]["access_console_log"].upper() if PROJECT_CONFIG["log"]["access_console_log"] else None,
            "enqueue": True,
            "backtrace": False,
            "diagnose": True,
            "catch": True,
            "filter": lambda record: record["extra"].get("name", None) == "access",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>ACCESS</cyan> - <level>{message}</level>"
        },
        "access_file": {
            "sink": PROJECT_DIR.joinpath(PROJECT_CONFIG["log"]["file_path"], "access.log"),
            "rotation": "3 MB",
            "retention": datetime.timedelta(hours=float(PROJECT_CONFIG["log"].get("retention", 168))),
            "level": PROJECT_CONFIG["log"]["access_file_log"].upper() if PROJECT_CONFIG["log"]["access_file_log"] else None,
            "enqueue": True,
            "backtrace": False,
            "diagnose": True,
            "encoding": "utf-8",
            "catch": True,
            "filter": lambda record: record["extra"].get("name", None) == "access",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>ACCESS</cyan> - <level>{message}</level>"
        },
    }
}
__logger.remove()
LOGGERS_ID = {
    key: __logger.add(**handler_)
    for key, handler_ in LOGGER_CONFIG["handlers"].items()
    if handler_["level"]
}
__logger.success(f"Loggers: {LOGGERS_ID}")

DEFAULT_TIMEZONE = "UTC"
LOCAL_TIMEZONE = "Asia/Shanghai"

DATABASE_NAME = os.getenv("FS_DATABASE_NAME", PROJECT_CONFIG["database"]["db_name"])
DATABASE_CONFIG = {
    "connections": {
        "master": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("FS_MASTER_DATABASE_HOST", PROJECT_CONFIG["database"]["master"]["host"]),  # FS_DATABASE_HOST 数据库名称环境变量根据需求修改
                "port": int(os.getenv("FS_MASTER_DATABASE_PORT", PROJECT_CONFIG["database"]["master"]["port"])),
                "user": os.getenv("FS_MASTER_DATABASE_USER", PROJECT_CONFIG["database"]["master"]["user"]),
                "password": os.getenv("FS_MASTER_DATABASE_PASSWORD", PROJECT_CONFIG["database"]["master"]["password"]),
                "database": os.getenv("FS_DATABASE_NAME", PROJECT_CONFIG["database"]["db_name"]),
                "minsize": PROJECT_CONFIG["database"]["minsize"],
                "maxsize": PROJECT_CONFIG["database"]["maxsize"],
                "charset": "utf8mb4",
                "pool_recycle": PROJECT_CONFIG["database"]["pool_recycle"],
            }
        },
        "slave": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("FS_SLAVE_DATABASE_HOST", PROJECT_CONFIG["database"]["slave"]["host"]),  # FS_DATABASE_HOST 数据库名称环境变量根据需求修改
                "port": int(os.getenv("FS_SLAVE_DATABASE_PORT", PROJECT_CONFIG["database"]["slave"]["port"])),
                "user": os.getenv("FS_SLAVE_DATABASE_USER", PROJECT_CONFIG["database"]["slave"]["user"]),
                "password": os.getenv("FS_SLAVE_DATABASE_PASSWORD", PROJECT_CONFIG["database"]["slave"]["password"]),
                "database": os.getenv("FS_DATABASE_NAME", PROJECT_CONFIG["database"]["db_name"]),
                "minsize": PROJECT_CONFIG["database"]["minsize"],
                "maxsize": PROJECT_CONFIG["database"]["maxsize"],
                "charset": "utf8mb4",
                "pool_recycle": PROJECT_CONFIG["database"]["pool_recycle"],
            }
        },
    },
    "apps": {
        # 1.注意此处的app代表的并不与FastAPI的routers对应，为Tortoise中的app概念
        # 2.在Tortoise-orm使用外键时，需要用到该app名称来指执行模型，"app.model"，所以同一个app中不要出现名称相同的两个模型类
        # 3.app的划分结合 规则2与实际情况进行划分即可
        "user_model": {
            "models": [
                "src.faster.routers.user.models",
            ],
            "default_connection": "master",
        },
    },
    "routers": ["src.my_tools.tortoise_tools.routers.WriteOrReadRouter"],
    "use_tz": True,  # 设置数据库总是存储utc时间
    "timezone": DEFAULT_TIMEZONE,  # 设置时区转换，即从数据库取出utc时间后会被转换为timezone所指定的时区时间（待验证）
}

# 仅开发时需要记录迁移情况
DEV and DATABASE_CONFIG["apps"].update(
    {
        "aerich": {
            "models": ["aerich.models"],
            "default_connection": "master",
        }
    }
)


HTTP_REQUEST_JSON_HEADER = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}
