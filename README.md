# FastAPI示例框架

> 项目的开发说明参考`documents/开发手册.md`，其中介绍了各个框架在开发中的使用方法等。
>
> 书写此项目时使用到的各个工具版本参考`documents/dev_requirements.txt`文件。
>
> 项目采用Tortoise-orm,以CBV视图形式提供接口
## 1 项目结构

本项目目录结构如下，其中`*`标为目录，以下出现的目录为项目必须文件，不允许添加git忽略：

```
├── main.py
├── setup.py
├── migrations *
├── project_env
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .dockerignore
├── docker *
│   ├── build_dockerfile
│   └── python_dockerfile
├── documents *
│   └── dev.md
└── src *
```

### 1.1 项目依赖文件

- project_env：环境变量文件，启动时从该文件中加载环境变量。
- pyproject.toml：项目配置文件，包括一些开发依赖包Commitizen和Aerich的配置也包括在内。
- requirements.txt：python的依赖文件，记录安装的包。
- docker：此目录包含docker打包镜像时使用的配置文件。
  - build_dockerfile：打包cx_Freeze编译结果为docker镜像的配置文件。
  - python_dockerfile：打包项目python源码为docker镜像的配置文件。
- .dockerignore: docker忽略的配置文件。
- .gitignore: git忽略的配置文件。

### 1.2 项目启动文件

- main.py: 程序入口文件，从`src`目录中导入`Application`。
- setup.py: cx_Freeze编译的脚本文件，使用`python setup.py build`调用编译程序，编译结果会生成在`./build`目录中。

### 1.3 忽略目录

除了项目的基本结构外，在项目运行或编译过程中还会产生一些其他目录，这些目录**应该**被git忽略，结构如下：

```
...
├── build *
├── logs *
...
```

- build: 编译结果目录，git应该忽略，但是使用build_dockerfile文件进行docker镜像的打包时，改目录**不应该**被`.dockerignore`文件忽略。
- logs: 运行日志文件目录，git和docker都应该忽略。

### 1.4 源码目录

项目开发源码在`src`目录下，其目录结构如下：

```
└── src *
    ├── __init__.py
    ├── application.py
    ├── settings.py
    ├── version.py
    ├── faster *
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── events.py
    │   ├── exceptions.py
    │   ├── middlewares.py
    │   └── routers *
    ├── my_tools *
    │   ├── __init__.py
    │   ├── password_tools.py
    │   ├── regex_tools.py
    │   ├── singleton_tools.py
    │   ├── fastapi_tools *
    │   └── tortoise_tools *
    └── my_apps *
```

- application.py: Typer的终端应用程序文件，用于启动FastAPI的服务。
- settings.py: 项目运行的配置文件。
- faster: FastAPI项目目录。

  - apps.py: FastAPI的实例文件。
  - events.py: FastAPI的startup与shutdown事件回调函数文件。
  - exceptions.py: FastAPI的异常回调函数文件, 分类捕获。
  - middlewares.py: FastAPI的中间件文件。
  - routers: FastAPI所有的子路由目录
    - models.py: 数据库的orm模型文件。
    - routers.py: 视图函数文件。
    - schemas.py: 视图函数接收和响应数据的序列化schema类文件。
    - validators: 数据库orm模型字段的验证器文件。
- my_tools: 工具包目录

  - singleton_tools.py: 单例模式工具
  - fastapi_tools: FastAPI的CBV工具
  - tortoise_tools: Tortoise一些扩展工具
- my_apps：其他服务




## 2 规范

### 2.1 git提交

- git的提交统一使用Commitizen，并在每次打包前使用`cz bump`命令生成CHANGELOG。
- git的tag_format格式为`VERSION-PROJECT`，PROJECT为项目代号，VERSION为版本，每个新的项目都从`0.0.0`开始，需要在`pyprojcet.toml`中配置。

### 2.2 docker规范

- docker镜像的tag保持和git的tag一致。
- 一般用`build_dockerfile`进行打包，根据项目情况灵活选择。
