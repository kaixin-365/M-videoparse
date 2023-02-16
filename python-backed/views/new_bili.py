from re import match,I
from httpx import Limits,AsyncClient
from router.router import router
from services.redis import redis,bili_cid_redis
from fastapi import Response

# 一些常量
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'accept-encoding': 'gzip',
    'cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Real-IP': '120.2.5.6',
    #'cookie': 'CURRENT_QUALITY=120;SESSDATA=', # 现在需要cookie 去取1080p流，否则只能取480p流
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) \
Version/13.0.3 Mobile/15E148 Safari/604.1'
}

cid_url = 'http://api.bilibili.com/x/player/pagelist'

video_api_url = 'http://api.bilibili.com/x/player/playurl'

info_data = ''
cid_cache = ''

#创建HTTP长连接池
client = AsyncClient(limits=Limits(keepalive_expiry=120))

async def get_cid(vid: str,p :int,isav: bool):
    global cid_cache,info_data
    cid_cache = await bili_cid_redis.hget(f'{vid}', key = str(p))
    if cid_cache is not None:
        cid = int(cid_cache)
        return cid

    if cid_cache is None:
        if isav is False:
            cid_json = await client.get(url=cid_url, params={'bvid':vid}, headers=headers, timeout=5)
        else:
            cid_json = await client.get(url=cid_url, params={'aid':vid[2:]}, headers=headers, timeout=5)
        try:
            cid_json = cid_json.json()
        except:
            return "(X_X) 服务器获取CID出错"
        if cid_json['code'] != 200:
            return "(?_?) 视频状态异常"
        info_data = cid_json['data']
        cid = int(cid_json['data'][p - 1]['cid'])
        return cid

async def set_cid_cache(vid: str,p: int):
    if cid_cache is None:
        page_list = []
        cid_list = []
        for pages in info_data:
            page_list.append(pages['page'])
        for cids in info_data:
            cid_list.append(cids['cid'])
        cache_dict=dict(zip(page_list,cid_list))
        await bili_cid_redis.hset(f'{vid}', mapping = cache_dict)

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

    if isav is False:
        link_json1 = await client.get(url=video_api_url,params=video_api_parms_bv,headers=headers,timeout=5)
    else:
        link_json1 = await client.get(url=video_api_url,params=video_api_parms_av,headers=headers,timeout=5)
    try:
        link_json = link_json1.json()
        url = link_json['data']['durl'][0]['url']
    except:
        return f"(X_X) 服务器获取视频链接出错,请刷新重试"
    return url

@router.get('/bili/{vid}')
async def bili_main(vid: str, p: int = 1):
    match_av = match(r'av', vid, I)
    match_bv = match(r'bv', vid, I)
    if vid is None:
        return '(?_?)请输入VID'

    if match_bv is None and match_av is None:
        return '(!_!) 输入视频号错误！'

    cache = await redis.get(f"bili{vid}p={p}")
    if cache is not None:
            return Response(status_code=307,
                            headers={
                                "Location": cache,
                                "Content-Type": "video/mp4",
                                "Cache-Control": "no-cache",
                                "Referrer-Policy": "no-referrer",
                                "X-Cache-used": "Yes"})

    if cache is None:
        if match_bv:
            cid = await get_cid(vid, p, False)
            url = await get_video_link(vid, cid ,False)
        if match_av:
            cid = await get_cid(vid, p, True)
            url = await get_video_link(vid, cid, True)

        head = url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={
                                        "Location": url,
                                        "Content-Type": "video/mp4",
                                        "Cache-Control": "no-cache",
                                        "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set(f"bili{vid}p={p}", url, ex=120)
                await set_cid_cache(vid,p)
        else:
            try:
                return url
            finally:
                await bili_cid_redis.delete(vid)