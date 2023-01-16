from fastapi import APIRouter

router = APIRouter()

# 在此注册views下的api处理程序

from views.new_bili import *
from views.weibo import *
from views.acfun import *
from views.lanzou import *
from views.tieba import *
from views.pan_123pan import *
from views.haokan import *