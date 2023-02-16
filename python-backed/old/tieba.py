from re import findall
from httpx import AsyncClient
from router.router import router
from services.redis import *
from fastapi import Response

headers = {
        'Accept': 'text/html,*/*;q=0.8',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
url = 'https://tieba.baidu.com/p/'
#创建HTTP长连接池
client = AsyncClient()

async def GetTieba(vid: int):
    try:
        resp = await client.get(url=url + str(vid), headers=headers, timeout=5)
        html = resp.text
    except:
        return '(X_X) 服务器访问出错'

    vlink = findall(r'data-video="([^"]+)', html)[0]
    return vlink

@router.get('/tieba/{vid}')
async def tiebalocation(vid: int):
    if vid is None:
        return '(?_?) 请输入VID'

    cache = await redis.get("tieba" + f"{vid}")
    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    else:
        link_url = await GetTieba(vid)
        head = link_url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={"Location": link_url,
                                         "Content-Type": "video/mp4",
                                         "Cache-Control": "no-cache",
                                         "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set("tieba" + f"{vid}", link_url, ex=600)
