import re
import httpx
from router.router import router
from services.redis import *
from fastapi import Response

# 一些常量
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'dnt': '1;',
    #'origin': 'https://m.bilibili.com',
    'pragma': 'no-cache',
    'referer': 'https://m.bilibili.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) \
Version/13.0.3 Mobile/15E148 Safari/604.1'
}

cid_url = 'http://api.bilibili.com/x/player/pagelist'

video_api_url = 'http://api.bilibili.com/x/player/playurl'


async def get_av_cid(avid: str,p :int):

    async with httpx.AsyncClient() as client:
        try:
            cid_json = await client.get(url=cid_url, params={'aid':avid[2:]}, headers=headers, timeout=5)
            cid_json = cid_json.json()
            return_code = cid_json['code']
        except:
            return "(X_X) 服务器出错！1"

    if return_code == -404:
        return "(?_?) 视频不存在！"

    cid = int(cid_json['data'][p - 1]['cid'])

    return cid

async def get_bv_cid(bvid: str,p :int):

    async with httpx.AsyncClient() as client:
        try:
            cid_json = await client.get(url=cid_url, params={'bvid':bvid}, headers=headers, timeout=5)
            cid_json = cid_json.json()
            return_code = cid_json['code']
        except:
            return "(X_X) 服务器出错！1"

    if return_code == -404:
        return "(?_?) 视频不存在！"

    cid = int(cid_json['data'][p - 1]['cid'])

    return cid

async def get_video_link(vid :str,cid: int,isav: bool):

    video_api_parms_av = {
    'platform': 'html5',
    'cid':cid,
    'avid':vid[2:],
    'type': 'mp4',
    'qn': '208',
    'high_quality': '1'
    }

    video_api_parms_bv = {
    'platform': 'html5',
    'cid':cid,
    'bvid':vid,
    'type': 'mp4',
    'qn': '208',
    'high_quality': '1'
    }

    async with httpx.AsyncClient() as client:
        try:
            if isav is False:
                link_json = await client.get(url=video_api_url,params=video_api_parms_bv,headers=headers,timeout=5)
            else:
                link_json = await client.get(url=video_api_url,params=video_api_parms_av,headers=headers,timeout=5)

            link_json = link_json.json()
            url = link_json['data']['durl'][0]['url']
        except:
            return "(X_X) 服务器出错！2"

    return url

@router.get('/bili/{vid}')
async def bili_location(vid: str, p: int = 1):

    match_av = re.match(r'av', vid, re.I)
    match_bv = re.match(r'bv', vid, re.I)

    if vid is None:
        return '(?_?)请输入VID'
    if match_bv is None and match_av is None:
        return '(!_!) 输入视频号错误！'

    cache = await redis.get("bili" + f"{vid}" + f"?p={p}")

    if cache is not None:

        return Response(status_code=307,
                        headers={
                            "Location": cache,
                            "Content-Type": "video/mp4",
                            "Cache-Control": "no-cache",
                            "Referrer-Policy": "no-referrer",
                            "X-Cache-used": "Yes"})

    while match_av is not None:

        cid = await get_av_cid(vid, p)
        url = await get_video_link(vid, cid, True)

        head = url[0:8]
        if head == 'https://':
            await redis.set("bili" + f"{vid}" + f"?p={p}", url, ex=600)
            return Response(status_code=307,
                            headers={
                                "Location": url,
                                "Content-Type": "video/mp4",
                                "Cache-Control": "no-cache",
                                "Referrer-Policy": "no-referrer"})
        else:
            return url

    while match_bv is not None:

        cid = await get_bv_cid(vid, p)
        url = await get_video_link(vid, cid ,False)

        head = url[0:8]
        if head == 'https://':

            await redis.set("bili" + f"{vid}" + f"?p={p}", url, ex=600)
            return Response(status_code=307,
                            headers={
                                "Location": url,
                                "Content-Type": "video/mp4",
                                "Cache-Control": "no-cache",
                                "Referrer-Policy": "no-referrer"})
        else:
            return url