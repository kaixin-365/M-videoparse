import json
import re
import httpx
from router.router import router
from services.redis import *
from fastapi import Response, Query

# 创建HTTP长连接池
client = httpx.AsyncClient()

parms = {
    'quickViewId' : 'videoInfo_new',
    'ajaxpipe':'1',
    #'reqID':'2'
    #'t':'当前UNIX时间'
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

async def get_link(vid: str, is4k:bool, isJson:bool):
    try:
        html_doc = await client.get(url = f'https://www.acfun.cn/v/{vid}',params=parms,headers = headers,timeout=8)
        html_doc = html_doc.text.split('/*<!-- f')[0]
    except:
        return '服务器获取信息出错！可能视频不存在！'
    try:
        html_doc1 = str(json.loads(html_doc)['html']).split('= window.videoInfo =')[1]
        KS_json = json.loads(html_doc1.split('</script>')[0])['currentVideoInfo']['ksPlayJson']
        url_json = json.loads(KS_json)['adaptationSet'][0]['representation']
    except:
        return '获取链接过程出错！'

    url_dict = {}
    qualitys = ['1080p60','1080p+','1080p','720p60','720p','540p','360p']
    for k in range(len(url_json)):
        vjson = url_json[k]
        qualityType = vjson['qualityType']
        url = vjson['url']
        url_dict[qualityType] = url

    if isJson is True:
        return url_dict

    if is4k is True:
        try:
            return url_dict['2160p']
        except:
            return '此视频无4K清晰度！'
    if is4k is False:
        for k in qualitys:
            try:
                return url_dict[k]
                break
            except:
                pass

@router.get('/acfun/{vid}')
async def bili_location(vid: str, q: str = Query("1080p", min_length=2, max_length=5), isjson: int = 0):
    match_ac = re.match(r'ac', vid, re.I)
    if  match_ac is None:
        return '视频号输入错误！'

    cache = await redis.get("acfun" + f"{vid}" + '?q=' + q )

    while cache is not None:
        return Response(status_code=307,
                        headers={
                            "Location": cache,
                            "Content-Type": "application/vnd.apple.mpegurl",
                            "Cache-Control": "no-cache",
                            "Referrer-Policy": "no-referrer",
                            "X-Cache-used": "Yes"})
    if isjson == 1:
        json_cache = await redis.get("acfun" + f"{vid}" + '?q=' + q + 'json')
        if json_cache is None:
            await get_link(vid,True,True)
            try:
                return Response(status_code=200,
                                headers={
                                    "Content-Type": "application/json; charset=utf-8",
                                    "Cache-Control": "no-cache"})
            finally:
                await redis.set("acfun" + f"{vid}" + '?q=' + q + 'json', url, ex=120)
        else:
            return json_cache


    while cache is None and match_ac is not None:
        if q == '1080p':
            url = await get_link(vid,False,False)
            head = url[0:8]
            if head == 'https://':
                try:
                    return Response(status_code=307,
                                    headers={
                                        "Location": url,
                                        "Content-Type": "application/vnd.apple.mpegurl",
                                        "Cache-Control": "no-cache",
                                        "Referrer-Policy": "no-referrer"})
                finally:
                    await redis.set("acfun" + f"{vid}" + '?q=' + q, url, ex=600)
            else:
                return url

        
        if q == '4k':
            url = await get_link(vid,True,False)
            head = url[0:8]
            if head == 'https://':
                try:
                    return Response(status_code=307,
                                    headers={
                                        "Location": url,
                                        "Content-Type": "application/vnd.apple.mpegurl",
                                        "Cache-Control": "no-cache",
                                        "Referrer-Policy": "no-referrer"})
                finally:
                    await redis.set("acfun" + f"{vid}" + '?q=' + q, url, ex=600)
            else:
                return url
