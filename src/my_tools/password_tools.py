# -*- coding: utf-8 -*-
# @Time    : 2021/11/25 14:37
# @Author  : NotBeBarnon
# @Description :
import hashlib


def make_password(password: str):
    return hashlib.md5(password.encode(encoding="ascii")).hexdigest()


if __name__ == '__main__':
    pass
