import re
import httpx
from router.router import router
from services.redis import *
from fastapi import Response

headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'DNT': '1',
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
url = 'https://tieba.baidu.com/p/'


async def GetTieba(vid: int):
    global url
    global headers

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url=url + str(vid), headers=headers, timeout=5)
            html = resp.text
        except:
            return '(X_X) 服务器访问出错'
        finally:
            await client.aclose()

    vlink = re.findall(r'data-video="([^"]+)', html)[0]
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
            await redis.set("tieba" + f"{vid}", link_url, ex=600)
            return Response(status_code=307,
                            headers={"Location": link_url,
                                     "Content-Type": "video/mp4",
                                     "Cache-Control": "no-cache",
                                     "Referrer-Policy": "no-referrer"})
