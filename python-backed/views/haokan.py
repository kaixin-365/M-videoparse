from httpx import AsyncClient
from json import loads
from lxml import etree
from urllib.parse import urlsplit
from random import randint
from router.router import router
from services.redis import haokan_redis
from fastapi import Response

client = AsyncClient()

async def getvideolink(vid: int):
    url = 'http://vv.baidu.com/v'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.8,*/*;q=0.8',
        'cache-control': 'no-cache',
        'Connection': 'keep-alive',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    html = await client.get(url=url, params={'vid':vid}, headers=headers, timeout=5)
    data = etree.HTML(html.text)
    data = data.xpath('//*[@id="_page_data"]')
    info_json = str(data[0].text).split('_ = ')[1]
    info_json = loads(info_json.split(';')[0])['curVideoMeta']['clarityUrl']

    qualitys = ['蓝光','超清','高清','标清']
    url_dict = {}
    for i in info_json:
        url_split = urlsplit(i['url'])
        url = f'{url_split[0]}://{url_split[1]}{url_split[2]}'
        quality = i['title']
        url_dict[quality] = url

    for k in qualitys:
        try:
            return url_dict[k]
        except:
            pass

async def set_cache(vid: int, value: str):
    try:
        await haokan_redis.set(f'haokan{vid}',value)
    except:
        print('设置缓存出错！')

@router.get('/haokan/{vid}')
async def haokan_main(vid: int):
    cache = await haokan_redis.get(f'haokan{vid}')
    if cache is not None:
        url = f'https://vd{randint(1,4)}.bdstatic.com{cache}'
        return Response(status_code=307,
                            headers={
                                "Location": url,
                                "Content-Type": "video/mp4",
                                "Cache-Control": "no-cache",
                                "Referrer-Policy": "no-referrer",
                                "X-Cache-used": "Yes"})
    
    if cache is None:
        try:
            url = await getvideolink(vid)
            return Response(status_code=307,
                            headers={
                                "Location": url,
                                "Content-Type": "video/mp4",
                                "Cache-Control": "no-cache",
                                "Referrer-Policy": "no-referrer",
                                "X-Cache-used": "Yes"})
        except:
            return '获取链接出错！'
        finally:
            value = urlsplit(url)[2]
            await set_cache(vid,value)

