# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 17:01
# @Author  : NotBeBarnon
# @Description :
import argparse
import json
import logging
import os
import platform
import re
import sys
from pathlib import Path
from typing import List, Iterator

import tomlkit
from cx_Freeze import setup, Executable

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s  - <%(filename)s>")

PROJECT_DIR: Path = Path(__file__).parent
with open(PROJECT_DIR.joinpath("pyproject.toml"), "r", encoding="utf-8") as toml_file:
    toml_config_ = tomlkit.load(toml_file)
PROJECT_CONFIG = json.loads(json.dumps(toml_config_))  # 转换包装类型为Python默认类型

logging.info(f"PROJECT_DIR: {PROJECT_DIR}")


def build():
    # 三个读取依赖的工具方法
    def get_python_packages(file_path: Path) -> Iterator[str]:
        """
        查找目录下所有python包
        """
        if not file_path.is_dir():
            return
        for child in file_path.iterdir():
            if child.is_dir():
                if is_python_package := set(child.glob("__init__.py")):
                    # print(f"init-{is_python_package}")
                    yield child.name

    def get_all_packages() -> Iterator[str]:
        """
        获取site中所有的python包
        """
        site_regex = re.compile("[\\\\|/]site-packages")
        site_path = None
        for path in sys.path:
            if site_regex.search(path):
                site_path = Path(path)
        if site_path:
            yield from get_python_packages(site_path)

    def get_all_requirements() -> Iterator[str]:
        package_regex = re.compile("[a-zA-Z\-_]+")

        for line_content in open(PROJECT_DIR / "requirements.txt", "r"):
            if pack_name := package_regex.match(line_content):
                yield pack_name.group().replace("-", "_")

    # 添加依赖
    packages: List = PROJECT_CONFIG["tool"]["cx_freeze"]["packages"]
    if platform.system() == "Linux":
        packages.append("uvloop")

    requirements_str = "-".join(get_all_requirements())
    for pack in get_all_packages():
        if pack in requirements_str:
            packages.append(pack)

    build_exe_options = {
        "include_files": PROJECT_CONFIG["tool"]["cx_freeze"]["include_files"],
        "packages": packages,
        "excludes": PROJECT_CONFIG["tool"]["cx_freeze"]["excludes"],
        "includes": PROJECT_CONFIG["tool"]["cx_freeze"]["includes"],
    }
    logging.info(" ---- cx_Freeze build --------")
    setup(
        name=PROJECT_DIR.name,
        version=PROJECT_CONFIG["tool"]["commitizen"]["version"],
        description=PROJECT_DIR.name,
        options={"build_exe": build_exe_options},
        executables=[Executable("main.py")],
    )


def build_docker(version: str = None):
    logging.info(" ---- Docker build --------")

    if version:
        logging.info(f" ---- {version} build --------")
        tag_ = str(PROJECT_CONFIG["tool"]["build_docker"]["docker_repo"])
        dockerfile_ = str(PROJECT_CONFIG["tool"]["build_docker"]["dockerfile"])
        # 执行打包脚本
        os.system(f"cd {str(PROJECT_DIR.absolute())} && docker build -t {tag_}:{version} -f {dockerfile_} .")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rebuild my program")
    parser.add_argument("build_command", type=str, choices=["build", "docker"], help="Please input \"build\" or \"docker\"")
    parser.add_argument("-v", "--version", type=str, help="Please input <version:string> [eg: 1.0.1-rcu]")
    args = parser.parse_args()
    if args.build_command == "build":
        build()
    elif args.build_command == "docker":
        # 修改原始命令，否则cx_Freeze的setup无法正常执行
        sys.argv = sys.argv[:2]
        sys.argv[1] = "build"
        build()
        build_docker(args.version)
