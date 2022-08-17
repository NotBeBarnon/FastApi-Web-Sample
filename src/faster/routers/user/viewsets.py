# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:16
# @Author  : NotBeBarnon
# @Description :
import asyncio

import arrow
import orjson
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette import status
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.functions import Count

from src.my_tools.fastapi_tools import Action, BaseViewSet
from src.my_tools.password_tools import make_password
from src.settings import LOCAL_TIMEZONE
from .pydantics import *

user_routers = APIRouter(prefix=f"/{app_name}")


class UserViewSet(BaseViewSet):

    @Action("", methods=["POST"], response_model=UserIncludeCompanyAndPositionPydantic)
    async def create(self, user: UserCreatePydantic):
        """
        创建用户
        """

        create_dict_ = user.dict(exclude={"password_again"})
        create_dict_["password"] = make_password(user.password)
        # 生成uid
        pre_ = arrow.now(tz=LOCAL_TIMEZONE).format("YYMM")
        suf_ = await User.filter(uid__startswith=pre_).count()
        create_dict_["uid"] = f"{pre_}{suf_ + 1:05d}"
        user_obj = await User.create(**create_dict_)
        return await UserIncludeCompanyAndPositionPydantic.from_tortoise_orm(user_obj)

    # @redis_client(RedisNamespace.key(b"rcu_info:all"), Response(headers={"Content-Type": "application/json"}), ex_pttl=10000)
    @Action.get("/cache_sample")
    async def cache_sample(self):
        logger.info("<Key:cache_sample> visiting Database")
        await asyncio.sleep(0.5)
        # with redis_client.get_client(SentinelNodeEnum.master) as client:
        #     assert isinstance(client, Redis)
        #     await client.set(RedisNamespace.key(b"cache_sample"), orjson.dumps({"success": "Hello World!"}), ex=10)
        return Response(
            content=orjson.dumps({"success": "Hello World!"}),
            headers={
                "Content-Type": "application/json",
                # "No-Cache": "no_cache",
            }
        )

    @Action.get("/cache_query_list")
    async def cache_query_list(self, beams: List[int]):
        pass

    @Action("/all", methods=["GET"], response_model=List[UserIncludeCompanyAndPositionPydantic])
    async def all(self, response: Response):
        """
        查询所有用户
        """
        response.headers["No-Cache"] = "no_cache"
        return await UserIncludeCompanyAndPositionPydantic.from_queryset(User.all())

    @Action("/{uid}", methods=["GET"], response_model=UserIncludeCompanyAndPositionPydantic,
            responses={404: {"model": HTTPNotFoundError}})
    async def get(self, uid: str):
        """
        查询用户信息
        """
        return await UserIncludeCompanyAndPositionPydantic.from_queryset_single(User.get(uid=uid))

    @Action("/{uid}", methods=["PATCH"], response_model=UserIncludeCompanyAndPositionPydantic,
            responses={404: {"model": HTTPNotFoundError}})
    async def update(self, uid: str, user: UserUpdatePydantic):
        """
        修改用户信息
        """
        # 密码加密
        update_dict_ = user.dict(exclude={"password_again"}, exclude_unset=True, exclude_defaults=True)
        if "password" in update_dict_:
            update_dict_["password"] = make_password(update_dict_["password"])
        await User.filter(uid=uid).update(**update_dict_)
        return await UserIncludeCompanyAndPositionPydantic.from_queryset_single(User.get(uid=uid))

    @Action("/{uid}", methods=["DELETE"], response_model=UserIncludeCompanyAndPositionPydantic,
            responses={404: {"model": HTTPNotFoundError}})
    async def delete(self, uid: str):
        """
        删除用户
        """
        user_obj = await User.get(uid=uid)
        deleted_count_ = await User.filter(uid=uid).delete()
        return await UserIncludeCompanyAndPositionPydantic.from_tortoise_orm(user_obj)


UserViewSet.register(user_routers)


class CompanyViewSet(BaseViewSet):
    model = Company
    schema = CompanyPydantic
    pk_name = "id"
    pk_type = int
    page_size = 10
    views = {
        "all": None,
        "create": CompanyCreatePydantic,
        "get": None,
        "update": CompanyUpdatePydantic,
        "delete": None,
    }

    @Action.get("/query_company_include_users", response_model=List[CompanyIncludeUsersPydantic])
    async def query_company_include_users(self, company_id: int = None):
        if company_id:
            return await CompanyIncludeUsersPydantic.from_queryset(Company.filter(id=company_id))
        return await CompanyIncludeUsersPydantic.from_queryset(Company.all())

    @Action.patch("/{company_id}/add_users", response_model=CompanyPydantic)
    async def add_users(self, company_id: int, users_info: List[CompanyAddUsersPydantic]):
        """为公司添加用户"""
        company_obj = await Company.get(id=company_id)
        position_set = set()
        user_set = set()
        users_obj = []
        for user_info_ in users_info:
            if user_info_.uid in user_set:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户uid不能重复")
            user_set.add(user_info_.uid)
            position_set.add(user_info_.position_id)
            users_obj.append(User(uid=user_info_.uid, position_id=user_info_.position_id, company_id=company_id))

        # 校验职位是否存在
        position_num_ = len(position_set)
        p_count_ = await Position.annotate(num_count=Count('id')).filter(id__in=position_set,
                                                                         company_id=company_id).limit(
            position_num_).first()
        if p_count_.num_count != position_num_:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="部分用户职位不存在")

        # 校验用户是否都存在
        user_num_ = len(user_set)
        u_count_ = await User.annotate(num_count=Count('uid')).filter(uid__in=user_set).limit(user_num_).first()
        if u_count_.num_count != user_num_:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="部分用户不存在")

        # 更新
        num_ = await User.bulk_update(users_obj, ["company_id", "position_id"], batch_size=10)
        return await CompanyPydantic.from_tortoise_orm(company_obj)


CompanyViewSet.register(user_routers)


class PositionDepends(object):

    @classmethod
    async def validator_info_of_create(cls, body: PositionCreatePydantic):
        if not await Company.exists(id=body.company_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所选公司不存在")

        if body.higher_id:
            higher_position_obj = await Position.get_or_none(id=body.higher_id, company_id=body.company_id)
            if higher_position_obj is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所选上级职位在此公司不存在")

            if body.level <= higher_position_obj.level:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="职位级别必须小于上级职位")

        if await Position.exists(company_id=body.company_id, name=body.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="职位名称在此公司已存在")

        return body

    @classmethod
    async def validator_info_of_update(cls, pk: int, body: PositionUpdatePydantic):
        position_obj = await Position.get(id=pk)
        if body.name and await Position.exists(company_id=body.company_id, name=body.name, id__not=pk):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="职位名称在此公司已被其他职位使用")

        if body.higher_id or body.level:
            body.level = body.level or position_obj.level
            body.higher_id = body.higher_id or position_obj.higher_id

            higher_position_obj = await Position.get_or_none(id=body.higher_id, company_id=position_obj.company_id,
                                                             id__not=pk)
            if higher_position_obj is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所选上级职位在此公司不存在")

            if body.level <= higher_position_obj.level:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="职位级别必须小于上级职位")

        return body

    @classmethod
    async def validator_add_lowers(cls, pk: int, body: AddLowersPositionPydantic):
        position_obj = await Position.get(pk=pk)
        position_num_ = len(body.lowers)
        p_count_ = await Position.annotate(num_count=Count('id')).filter(id__in=body.lowers,
                                                                         company_id=position_obj.company_id).limit(
            position_num_).first()
        if p_count_.num_count != position_num_:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="部分职位不存在")
        if await Position.exists(id__in=body.lowers, level__lte=position_obj.level):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="下级职位级别必须比此职位小")
        return body


class PositionViewSet(BaseViewSet):
    model = Position
    schema = PositionPydantic
    pk_name = "id"
    pk_type = int
    page_size = 10
    views = {
        "all": None,
        "delete": None,
    }

    @Action.post("", response_model=PositionPydantic)
    async def create(self, body: PositionCreatePydantic = Depends(PositionDepends.validator_info_of_create)):
        """
        在指定公司创建一个职位
        - level: 职位级别，从1开始，1表示最高级
        """
        return await PositionPydantic.from_tortoise_orm(await Position.create(**body.dict(exclude_unset=True)))

    @Action.patch("/{pk}", response_model=PositionTreePydantic)
    async def update(self, pk: int, body: PositionUpdatePydantic = Depends(PositionDepends.validator_info_of_update)):
        await Position.filter(pk=pk).update(**body.dict(exclude_unset=True))
        return await PositionTreePydantic.from_queryset_single(Position.get(pk=pk))

    @Action.get("/{pk}", response_model=PositionTreePydantic)
    async def get(self, pk: int):
        return await PositionTreePydantic.from_queryset_single(Position.get(pk=pk))

    @Action.get("/tree", response_model=PositionTreePydantic)
    async def tree(self, company_id: int = None, level: int = None):
        """获取职位树状图"""
        filter_dict = {"higher_id": None}
        if company_id:
            filter_dict["company_id"] = company_id
        if level:
            filter_dict["level"] = level

        return await PositionTreePydantic.from_queryset(Position.filter(**filter_dict))

    @Action.post("/{pk}/add_lowers", response_model=PositionTreePydantic)
    async def add_lowers(self, pk: int,
                         body: AddLowersPositionPydantic = Depends(PositionDepends.validator_add_lowers)):
        await Position.filter(pk__in=body.lowers).update(higher_id=pk)
        return await PositionTreePydantic.from_queryset_single(Position.get(pk=pk))


PositionViewSet.register(user_routers)


class QuerySetTestViewSet(BaseViewSet):

    @Action.get("/all_values")
    async def all_values(self):
        """
        values方法查询所有用户
        """
        resp = await User.all().values("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/get_values/{uid}")
    async def get_values(self, uid: str):
        """
        values方法查询单个用户
        - uid: 用户uid
        """
        resp = await User.get(uid=uid).values("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/all_values_list")
    async def all_values_list(self):
        """
        values_list方法查询所有用户
        """
        resp = await User.all().values_list("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/single_exists/{uid}")
    async def exists(self, uid: str):
        """
        直接使用Model的exists方法判断用户是否存在
        - uid: 用户id
        """
        return await User.exists(uid=uid)

    @Action.get("/filter_exists/{uid}")
    async def filter_exists(self, uid: str):
        """
        使用filter+exists
        - uid: 用户id
        """
        return await User.filter(uid=uid).exists()


QuerySetTestViewSet.register(user_routers)


class DependsTestDepends(object):

    @classmethod
    async def get_user(cls, uid: str = None):
        if uid is not None:
            return await User.get(uid=uid)


class DependsTestViewSet(BaseViewSet):

    @Action.get("/depends", response_model=UserIncludeCompanyAndPositionPydantic)
    async def depends(self, user_obj: User = Depends(DependsTestDepends.get_user), company: int = None):
        """
        Depends测试
        """
        if user_obj:
            return await UserIncludeCompanyAndPositionPydantic.from_tortoise_orm(user_obj)
        else:
            return ORJSONResponse(status_code=status.HTTP_201_CREATED)


DependsTestViewSet.register(user_routers)
