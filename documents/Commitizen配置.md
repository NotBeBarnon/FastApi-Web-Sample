# Commitizen

## 1 安装

> 建议将commitizen安装到系统级别的python环境中，这样不需要激活虚拟环境也可以使用Commitizen的命令。

使用`pip install commitizen`安装即可。



## 2 配置

在项目根目录下`pyproject.toml`文件中关于Commitizen的内容如下:

```toml
[tool.commitizen]
name = "cz_conventional_commits" # 默认即可
version = "0.0.0" # 项目版本号
version_files = [  # 项目版本号存储变量 [非必须]
    "src/version.py:VERSION",
]
tag_format = "$version-sample"  # 项目Tag格式 -后面跟项目名称
use_shortcuts = true # 启用cz c命令时的快捷键 [非必须]
update_changelog_on_bump = true # bump自动生成changelog
annotated_tag = true # bump时自动生成标签
```



## 3 优化 

> 如果安装版本 大于2.20.0则**不需要**进行优化
>
> Commitizen的版本如果 **小于2.20.0(仅测试到此版本)** 则必须对Commitizen进行源码优化，否则Commitizen在识别Tag的名称时，对`version (eg: v1.0.0)`占比低的Tag会识别失败。

首先在安装Commitizen的python环境中，输出`sys.path`的内容。

```shell
C:\ python
>>> import sys
>>> print(sys.path)

['', ...
'name\\lib\\site-packages']
```

进入到上述的`name\\lib\site-packages\\commitizen`目录中。

修改此目录中`commands/changelog.py`文件中的`第64行`，将`tag.name`与`latest_version`使用正则表达式匹配出主要的version版本：

```python
# commands/changelog.py

# 62 line
tag_ratio = map(
  lambda tag: (SequenceMatcher(None, latest_version, tag.name).ratio(), tag),
  tags,
)
# 64 line  -> try:

# 修改为 >>>
import re
version_regex = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
tag_ratio = map(
  lambda tag: (
    SequenceMatcher(None,
                    version_regex.search(latest_version).group(),
                    version_regex.search(tag.name).group()).ratio(),
    tag,
  ),
  tags
)
```







