# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:00
# @Author  : NotBeBarnon
# @Description :
from enum import Enum, IntEnum

from tortoise import fields, models

from src.my_tools.regex_tools import chinese_regex
from . import app_name


class User(models.Model):
    """
    用户
    """

    user_number = fields.IntField(null=True, description="用户编号")
    uid = fields.CharField(max_length=10, unique=True, description="用户UID，唯一标识用户", pk=True)
    username = fields.CharField(max_length=32, description="用户名")
    password = fields.CharField(max_length=64, description="密码")

    name = fields.CharField(max_length=32, null=True, description="用户的名字")
    family_name = fields.CharField(max_length=32, null=True, description="用户的姓氏")

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    modified_at = fields.DatetimeField(auto_now=True, description="修改时间")

    company = fields.ForeignKeyField("user_model.Company", null=True, related_name="users", description="所属公司", on_delete=fields.SET_NULL)
    position = fields.ForeignKeyField(
        "user_model.Position",
        null=True,
        related_name="users",
        description="所属职位",
        on_delete=fields.SET_NULL,
    )

    def full_name(self) -> str:
        """
        用户全名
        """
        if self.name or self.family_name:
            if chinese_regex.search(f"{self.name}") or chinese_regex.search(f"{self.family_name}"):
                return f"{self.family_name or ''}{self.name or ''}".strip()
            return f"{self.name or ''} {self.family_name or ''}".strip()
        return self.username

    class PydanticMeta:
        computed = ("full_name",)
        exclude = ("user_number", "created_at", "modified_at", "full_name")  # 用以演示computed无法通过exclude排除

        # allow_cycles = True
        # max_recursion = 1

    class Meta:
        table = f"{app_name}_user"


class PositionLevelEnum(IntEnum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7


class Position(models.Model):
    name = fields.CharField(max_length=32, description="职位名称")
    level = fields.IntEnumField(enum_type=PositionLevelEnum, description="职位级别")
    company = fields.ForeignKeyField("user_model.Company", related_name="positions", description="所属公司", on_delete=fields.CASCADE)

    higher = fields.ForeignKeyField(
        "user_model.Position",
        null=True,
        related_name="lowers",
        description="上级职位",
        on_delete=fields.SET_NULL,
    )
    lowers: fields.ReverseRelation["Position"]
    users: fields.ReverseRelation["User"]

    class PydanticMeta:
        allow_cycles = True  # 允许循环引用，外键关联

    #   max_recursion = 1  # 最大递归深度

    class Meta:
        table = f"{app_name}_position"


class Company(models.Model):
    """
    公司
    """
    name = fields.CharField(max_length=32, description="公司名称")

    user: fields.ReverseRelation["User"]
    positions: fields.ReverseRelation["Position"]

    # class PydanticMeta:
    #     allow_cycles = True  # 允许循环引用，外键关联

    #     max_recursion = 1  # 最大递归深度

    class Meta:
        table = f"{app_name}_company"
