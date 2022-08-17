# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:10
# @Author  : NotBeBarnon
# @Description :
from typing import List, Set

from pydantic import Field, validator, BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import *


class UserPydantic(pydantic_model_creator(User, name="UserPydantic", exclude=("password",))):
    pass


class CompanyInUserPydantic(
    pydantic_model_creator(
        Company,
        name="CompanyInUserPydantic",
        exclude=("users", "positions"),
    )
):
    pass


class PositionInUserIncludeNonePydantic(
    pydantic_model_creator(
        Position,
        name="PositionInUserPydantic",
        include=("id", "name"),
    )
):
    pass


class PositionInUserPydantic(
    pydantic_model_creator(
        Position,
        name="PositionInUserPydantic",
        exclude=("users", "company", "lowers", "higher"),
    )
):
    higher: PositionInUserIncludeNonePydantic = Field(None, description="上级职位")
    lowers: List[PositionInUserIncludeNonePydantic] = Field(None, description="下级职位")


class UserIncludeCompanyAndPositionPydantic(UserPydantic):
    """
    包括公司及职位信息的完整用户信息
    """
    position: PositionInUserPydantic = Field(None, description="职位")
    company: CompanyInUserPydantic = Field(None, description="公司")

    class Config:
        title = "UserIncludeCompanyAndPositionPydantic"


class UserIncludePositionPydantic(UserPydantic):
    position: PositionInUserIncludeNonePydantic = Field(None, description="职位")

    class Config:
        title = "UserIncludePositionPydantic"


class UserCreatePydantic(
    pydantic_model_creator(User, name="UserCreatePydantic", exclude=("uid", "company_id", "position_id"),
                           exclude_readonly=True)):
    """
    创建用户时输入的body格式
    """
    password_again: str = Field(..., description="重复输入验证密码")

    @validator("password_again")
    def password_again_validator(cls, password_again, values, **kwargs):
        if password_again != values["password"]:
            raise ValueError("两次密码不一致")
        return password_again

    class Config:
        title = "UserCreatePydantic"


class UserUpdatePydantic(
    pydantic_model_creator(User, name="UserUpdatePydantic", include=("name",), exclude_readonly=True)):
    """
    更新用户信息时输入的body格式
    """
    username: str = None
    password: str = None
    password_again: str = Field(None, description="再次验证密码")

    @validator("password")
    def password_validator(cls, password, values, **kwargs):
        return password

    @validator("password_again", always=True)
    def password_again_validator(cls, password_again, values, **kwargs):
        if "password" in values and password_again != values["password"]:
            raise ValueError("密码不一致")
        return password_again


class CompanyPydantic(pydantic_model_creator(Company, name="CompanyPydantic")):
    pass


class CompanyCreatePydantic(
    pydantic_model_creator(Company, name="CompanyCreatePydantic", exclude=("id",), exclude_readonly=True)):
    pass


class CompanyUpdatePydantic(
    pydantic_model_creator(Company, name="CompanyUpdatePydantic", exclude=("id",), exclude_readonly=True)):
    name: str = None


class CompanyAddUsersPydantic(BaseModel):
    uid: str = Field(..., description="用户的uid")
    position_id: int = Field(..., description="职位id")


class CompanyIncludeUsersPydantic(CompanyPydantic):
    users: List[UserIncludePositionPydantic] = Field(..., description="用户列表")

    class Config:
        title = "CompanyIncludeUsersPydantic"


class PositionPydantic(pydantic_model_creator(Position, name="PositionPydantic")):
    company: CompanyPydantic = Field(..., description="所属公司")
    higher_id: int = Field(None, description="上级职位id")


class PositionTreeBasePydantic(pydantic_model_creator(Position, name="PositionTreePydantic")):
    company_id: int = Field(..., description="公司id")


class Deepin2PositionTreeBasePydantic(PositionTreeBasePydantic):
    company_id: int = Field(..., description="公司id")
    lowers: List[PositionTreeBasePydantic] = Field(None, description="下级职位")


class PositionTreePydantic(PositionTreeBasePydantic):
    company_id: int = Field(..., description="公司id")
    lowers: List[Deepin2PositionTreeBasePydantic] = Field(None, description="下级职位")

    class Config:
        title = "PositionTreePydantic"


class PositionCreatePydantic(
    pydantic_model_creator(
        Position,
        name="PositionCreatePydantic",
        exclude_readonly=True,
    )
):
    company_id: int = Field(..., description="公司id")
    higher_id: int = Field(None, description="上级职位id")


class PositionUpdatePydantic(
    pydantic_model_creator(Position, name="PositionUpdatePydantic", exclude_readonly=True)
):
    name: str = None
    level: int = None
    higher_id: int = Field(None, description="上级职位id")


class AddLowersPositionPydantic(BaseModel):
    lowers: Set[int] = Field(..., description="下级职位id")
