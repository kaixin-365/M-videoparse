# Windows系统下运行会有import问题，可以参考下面方法指定其他模块
# import sys
# sys.path.append(r'C:\Users\Administrator\Documents\GitHub\M-videoparse\python-backed\router')
# sys.path.append(r'C:\Users\Administrator\Documents\GitHub\M-videoparse\python-backed\services')
# sys.path.append(r'C:\Users\Administrator\Documents\GitHub\M-videoparse\python-backed\views')

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from router import router

file_path = "python-backed/index.html" 
#exitfile_path = "index.html"  # 后端首页文件

app = FastAPI()  # 初始化fastapi

app.include_router(router.router)  # 注册后端路由


@app.get('/')  # 主页展示方法
async def hello():
    return FileResponse(file_path)

# Windows下运行需要此行代码，Linux下可保留
if __name__ == "__main__":
    # 启动服务，因为我们这个文件叫做 main.py，所以需要启动 main.py 里面的 app
    # 第一个参数 "main:app" 就表示这个含义，然后是 host 和 port 表示监听的 ip 和端口
    # 看服务器情况去选择是否开uvicorn的reload，因为开启后吃性能
    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)