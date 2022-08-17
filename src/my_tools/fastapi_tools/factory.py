# -*- coding: utf-8 -*-
# @Time    : 2021/12/16 9:14
# @Author  : NotBeBarnon
# @Description :
from typing import List, Type

from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.contrib.pydantic import PydanticModel
from tortoise.models import MODEL

from .decorators import Action


def generate_all(model: Type[MODEL], schema: Type[PydanticModel]):
    """
    生成视图集的all方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出的序列化

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.get("/all", response_model=List[schema])
    async def all(self):
        return await schema.from_queryset(model.all())

    all.__doc__ = f"Query all {model.__name__}"

    return all


def generate_create(model: Type[MODEL], schema: Type[PydanticModel], input_schema: Type[PydanticModel]):
    """
    生成视图集的create方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        input_schema: http视图输入的body序列化对象

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.post("", response_model=schema)
    async def create(self, body: input_schema):
        return await schema.from_tortoise_orm(await model.create(**body.dict()))

    create.__doc__ = f"Create {model.__name__}"
    return create


def generate_get(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type):
    """
    生成视图集的get方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.get(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def get(self, pk: pk_type):
        return await schema.from_queryset_single(model.get(pk=pk))

    get.__doc__ = f"Get {model.__name__} by primary key"

    return get


def generate_update(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type, input_schema: Type[PydanticModel]):
    """
    生成视图集的update方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型
        input_schema: http视图的body序列化

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.patch(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def update(self, pk: pk_type, body: input_schema):
        obj: MODEL = await model.get(pk=pk)
        obj.update_from_dict(body.dict(exclude_unset=True, exclude_defaults=True))
        await obj.save()
        return await schema.from_tortoise_orm(obj)

    update.__doc__ = f"Update {model.__name__} by primary key"

    return update


def generate_delete(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type):
    """
    生成视图集的delete方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.delete(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def delete(self, pk: pk_type):
        obj = await model.get(pk=pk)
        deleted_count_ = await model.filter(pk=pk).delete()
        return await schema.from_tortoise_orm(obj)

    delete.__doc__ = f"Delete {model.__name__} by primary key"

    return delete
