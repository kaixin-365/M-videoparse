import re
import httpx
from router.router import router
from services.redis import *
from fastapi import Response

headers = {
    'accept': 'application/json, text/javascript, */*',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/96.0.4664.110 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}


async def GetLanzou(url: str, password: str):
    global headers

    ReForHost = re.compile(r'.*lanzou.*.com')
    ReForHtml = re.compile(r'sign.*\_c')

    try:
        host = re.findall(ReForHost, url)[0]
    except:
        return '(!_!) 链接有误'

    headers['referer'] = url
    headers['origin'] = host

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers={'user-agent': headers['user-agent']},timeout=5)
            html = resp.text
        except:
            return '(X_X) 服务器访问出错'
        finally:
            await client.aclose()

    sign = re.findall(ReForHtml, html)[0].split('=')[1]
    post_data = {'action': 'downprocess', 'sign': sign, 'p': password}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url=host + '/ajaxm.php', data=post_data,
                                     headers=headers, timeout=5)
            url_json = resp.json()
            print(url_json)
        except:
            return '(X_X) 服务器发送数据出错'
        finally:
            await client.aclose()

    url = url_json['dom'] + '/file/' + url_json['url']
    return url


@router.get('/lanzou/')
async def lanzou_location(url: str, p: str):
    ReForUrl = re.match(r'.*lanzou.*.com/', url)
    ReForScheme = re.match(r'http', url)
    if ReForUrl is False or ReForScheme is False:
        return '(!_!) 链接有误'
    if p is None:
        return '(?_?) 请输入密码'
    if url is None:
        return '(?_?) 请输入链接'

    ReForHost = re.compile(r'.*lanzou.*.com')
    len_host = len(re.findall(ReForHost, url)[0])
    path = url[len_host + 1:]

    cache = await redis.get("lanzou" + f"{path}")
    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    else:
        url = await GetLanzou(url, p)
        head = url[0:8]
        if head == 'https://':
            await redis.set("lanzou" + f"{path}", url, ex=1800)
            return Response(status_code=307,
                            headers={"Location": url,
                                     "Content-Type": "video/mp4",
                                     "Cache-Control": "no-cache",
                                     "Referrer-Policy": "no-referrer"})
        else:
            return url
