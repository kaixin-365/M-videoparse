from httpx import AsyncClient
from router.router import router
from services.redis import *
from fastapi import Response
from urllib.parse import urlparse,parse_qs
from random import choice

headers = {
        'Accept': 'text/html,*/*;q=0.8',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
url = 'http://tieba.baidu.com/mg/p/getPbData?kz='

#创建HTTP长连接池
client = AsyncClient()

async def GetTieba(vid: int):
    try:
        resp = await client.get(url=url + str(vid), headers=headers, timeout=5)
        html = resp.json()
    except:
        return '(X_X) 服务器访问出错'

    vlink = html['data']['post_list'][0]['video_info']['video_url']
    if vlink[0:5] == 'https':
        pass
    else:
        vlink = 'https://' + vlink.split('http://')[0]
    return vlink

async def GetStaticTieba(vid: int):
    try:
        resp = await client.get(url=url + str(vid), headers=headers, timeout=5)
        html = resp.json()
    except:
        return '(X_X) 服务器访问出错'
    mp4_data = parse_qs(urlparse(html['data']['post_list'][0]['content'][1]['link']).query)
    mp4_path = ['tieba-movideo','tieba-smallvideo']
    mp4_name = mp4_data['video'][0]
    name_split_len = len(mp4_name.split("_"))
    if name_split_len == 3:
        return mp4_path[0] + '/' + mp4_name + '.mp4'
    else:
        return mp4_path[1] + '/' + mp4_name + '.mp4'

@router.get('/tieba/{vid}')
async def tiebalocation(vid: int ,org: int = 0):
    if vid is None:
        return '(?_?) 请输入VID'
    if org < 0:
        return '(?_?)'
    if org >= 1: 
        cache = await haokan_redis.get(f"tieba{vid}")
    if org == 0:
        cache = await redis.get(f"tieba{vid}")

    if cache is not None:
        if org == 0:
            return Response(status_code=307,
                            headers={"Location": cache,
                                     "Content-Type": "video/mp4",
                                     "Cache-Control": "no-cache",
                                     "X-Cache-used": "Yes",
                                     "Referrer-Policy": "no-referrer"})
        if org >=1:
            origin_host = ['https://su.bcebos.com/','https://bos.nj.bpc.baidu.com/']
            vhost = choice(origin_host)
            print(vhost + cache)
            return Response(status_code=307,
                            headers={"Location": vhost + cache,
                            "Content-Type": "video/mp4",
                            "Cache-Control": "no-cache",
                            "X-Cache-used": "Yes",
                            "Referrer-Policy": "no-referrer"})
    else:
        if org == 0:
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
                    await redis.set(f"tieba{vid}", link_url, ex=600)

        if org >= 1:
            link_url = await GetStaticTieba(vid)
            head = link_url[0:5]
            if head == 'tieba':
                origin_host = ['https://su.bcebos.com/','https://bos.nj.bpc.baidu.com/']
                vhost = choice(origin_host)
                print(vhost + link_url)
                try:
                    return Response(status_code=307,
                                    headers={"Location": vhost + link_url,
                                             "Content-Type": "video/mp4",
                                             "Cache-Control": "no-cache",
                                             "Referrer-Policy": "no-referrer"})
                finally:
                    await haokan_redis.set(f"tieba{vid}", link_url)

