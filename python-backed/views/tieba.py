import re
import requests
from router.router import router
from services.redis import *
from fastapi import Response

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 '
}
url = 'http://tieba.baidu.com/p/'


def GetTieba(vid: int):
    global url
    global headers
    try:
        html = requests.get(url=url + str(vid), headers=headers).text
        vlink = re.findall(r'data-video="([^"]+)', html)[0]
    except:
        return '(X_X) 服务器访问出错'

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
        link_url = GetTieba(vid)
        head = link_url[0:8]
        if head == 'https://':
            await redis.set("tieba" + f"{vid}", link_url, ex=3600)
            return Response(status_code=307,
                            headers={"Location": link_url,
                                     "Content-Type": "video/mp4",
                                     "Cache-Control": "no-cache",
                                     "Referrer-Policy": "no-referrer"})
