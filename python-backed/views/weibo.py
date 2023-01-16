from re import match
from httpx import AsyncClient
from json import dumps
from router.router import router
from services.redis import redis
from fastapi import Response, Query

api_url = 'https://h5.video.weibo.com/api/component'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) \
Version/13.0.3 Mobile/15E148 Safari/604.1'

}
#创建HTTP长连接池
client = AsyncClient(http2=True)

# aiohttp发送post请求不知道怎么避免被json格式化，只能使用httpx了
async def GetWeibo(vid: str, q: str):
    q = q.lower()
    params = {
        'page': f'/show/{vid}'
    }

    data = {"Component_Play_Playinfo": {"oid": f'{vid}'}}
    data_json = 'data=' + dumps(data)

    headers['Referer'] = f"https://h5.video.weibo.com/show/{vid}"
    headers['PAGE-REFERER'] = f"/show/{vid}"

    try:
        resp = await client.post(api_url, params=params, headers=headers,data=data_json, timeout=5)
        post = resp.json()
        post = post['data']['Component_Play_Playinfo']['urls']
    except:
        return "(X_X) 服务器获取链接出错！"

    if post is None:
        return "(?_?) 视频未公开或者不存在!"

    # 判断视频清晰度
    _4k_qualitys = ["超清 4K60","超清 4K","超清 2K60","超清 2K"]
    qualitys = ["高清 1080P","高清 720P","标清 480P","流畅 360P"]
    if q == '4k':
        for k in _4k_qualitys:
            try:
                raw_url = post[k]
                break
            except:
                pass
    if q =='1080p':
        for k in qualitys:
            try:
                raw_url = post[k]
                break
            except:
                pass

    if raw_url is None:
        return "(X_X) 出错啦！"

    url = 'https:' + raw_url
    return url


@router.get('/weibo/{vid}')
async def weibo_location(vid: str, q: str = Query("1080p", min_length=2, max_length=5)):
    vid_match = match(r'\d{4}:\d{16}', vid)
    if vid is None:
        return '(?_?)请输入VID'
    if vid_match is None:
        return "(!_!) 输入VID错误！"

    cache = await redis.get(f"WB-{vid}-q={q}")

    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    else:
        url = await GetWeibo(vid, q)
        head = url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={"Location": url,
                                         "Content-Type": "video/mp4",
                                         "Cache-Control": "no-cache",
                                         "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set(f"WB-{vid}-q={q}", url, ex=600)
        else:
            return url
