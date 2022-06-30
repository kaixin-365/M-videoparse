from fastapi import APIRouter

router = APIRouter()

# 在此注册views下的api处理程序

from views.bili import *
from views.weibo import *
from views.lanzou import *
from views.tieba import *
