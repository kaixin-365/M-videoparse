import re
import requests
import json
from router.router import router
from services.redis import *
from fastapi import Response, Query

api_url = 'https://h5.video.weibo.com/api/component'

# 'PAGE-REFERER': f'/show/{vid}'
# 'Referer': f'https://h5.video.weibo.com/show/{vid}',

headers = {
    'Host': 'h5.video.weibo.com',
    'Cache-Control': 'no-cache',
    'Content-Length': '64',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://h5.video.weibo.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Dest': 'empty',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}


def GetWeibo(vid: str, q: str):
    global api_url
    global headers
    # vid = vid
    q = q.lower()
    params = {
        'page': f'/show/{vid}'
    }
    data = {"Component_Play_Playinfo": {"oid": f"{vid}"}}
    headers['Referer'] = f"https://h5.video.weibo.com/show/{vid}"
    headers['PAGE-REFERER'] = f"/show/{vid}"
    post = requests.post(url=api_url, params=params, headers=headers, data="data=" + json.dumps(data), timeout=5).json()
    if post is None:
        return "(?_?) 视频未公开或者不存在!"
        # 判断视频清晰度
    if q == "4k":
        try:
            raw_url = post['data']['Component_Play_Playinfo']['urls']["超清 4K60"]
        except:
            try:
                raw_url = post['data']['Component_Play_Playinfo']['urls']["超清 4K"]
            except:
                return "(!_!) 该视频无4K源！"

    elif q == "2k":
        try:
            raw_url = post['data']['Component_Play_Playinfo']['urls']["超清 2K60"]
        except:
            try:
                raw_url = post['data']['Component_Play_Playinfo']['urls']["超清 2K"]
            except:
                return "(!_!) 该视频无2k源！"

    elif q == "1080p":
        try:
            raw_url = post['data']['Component_Play_Playinfo']['urls']["高清 1080P"]
        except:
            try:
                raw_url = post['data']['Component_Play_Playinfo']['urls']["高清 720P"]
            except:
                try:
                    raw_url = post['data']['Component_Play_Playinfo']['urls']["标清 480P"]
                except:
                    try:
                        raw_url = post['data']['Component_Play_Playinfo']['urls']["流畅 360P"]
                    except:
                        return "(X_X) 出错啦!"
    if raw_url is None:
        return "(X_X) 出错啦！"

    url = 'https:' + raw_url
    return url


@router.get('/weibo/{vid}')
async def weibo_location(vid: str, q: str = Query("1080p", min_length=2, max_length=5)):
    vid_match = re.match(r'\d{4}:\d{16}', vid)
    if vid is None:
        return '(?_?)请输入VID'
    if vid_match is None:
        return "(!_!) 输入VID错误！"

    cache = await redis.get("weibo" + f"{vid}" + f"?q={q}")

    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "Referrer-Policy": "no-referrer"})
    else:
        url = GetWeibo(vid, q)
        head = url[0:8]
        if head == 'https://':
            await redis.set("weibo" + f"{vid}" + f"?q={q}", url, ex=3600)
            return Response(status_code=307,
                            headers={"Location": url,
                                     "Content-Type": "video/mp4",
                                     "Cache-Control": "no-cache",
                                     "X-Cache-used": "Yes",
                                     "Referrer-Policy": "no-referrer"})
        else:
            return url
