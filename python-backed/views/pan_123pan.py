import httpx
from base64 import urlsafe_b64decode
from urllib.parse import urlparse
from router.router import router
from services.redis import *
from fastapi import Response

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'dnt': '1',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

info_api = 'https://www.123pan.com/a/api/share/get'
info_api_parms = {
    'limit':'100',
    'next':'1',
    'orderBy':'share_id',
    'orderDirection':'desc',
    #'shareKey':'',
    #'SharePwd':'',
    'ParentFileId':'0',
    'Page':'1'
}
file_url = 'https://www.123pan.com/a/api/share/download/info'

#创建HTTP长连接池
client = httpx.AsyncClient()


async def get_file_info(share: dict):

    global info_api_parms

    shareKey = info_api_parms['shareKey'] = share['ShareKey']

    try:
        pwd = info_api_parms['SharePwd'] = share['SharePwd']
    except:
        try:
            del info_api_parms['SharePwd']
        except:
            pass

    try:
        resp = await client.get(info_api,headers = headers,params=info_api_parms,timeout=5)
        html = resp.json()
    except:
        return '(X_X) 获取详情出错！1'

    try:
        info = html['data']['InfoList'][0]
    except:
        return '(X_X) 获取详情出错！2'
    info['ShareKey'] = shareKey
    try:
        info['pwd'] = pwd
    except:
        pass

    #print(info)
    return info

async def get_flie_url(info: dict):

    try:
        file_url_data = {
            "ShareKey":info['ShareKey'],
            "FileID":info['FileId'],
            "S3keyFlag":info['S3KeyFlag'],
            "Size":info['Size'],
            "Etag":info['Etag']
        }
    except:
        return '(X_X) 获取详情出错！3'

    other_headers = {
        'Content-Type':'application/json;charset=utf-8',
        #'Authorization':'Bearer undefined',
        #'Cookie': 'shareKey=' + info['ShareKey'] + '; SharePwd=' + info['pwd'],
        'origin': 'https://www.123pan.com',
        'Referer': 'https://www.123pan.com/s/' + info['ShareKey'],
        'platform': 'web',
        'app-version': '1.2'
    }

    post_headers = dict(headers, **other_headers)

    try:
        req = await client.post(file_url,data = file_url_data,headers = post_headers,timeout=5)
        resp = req.json()
    except:
        return '(X_X) 获取文件详情出错！'

    dev_url = urlparse(resp['data']['DownloadURL']).query
    url = urlsafe_b64decode(dev_url.split("params=")[1]).decode()
    #print(url)
    return url

# a = 'mag9-pAiUd'
# b = 'lufv'

@router.get('/123pan/{ShareKey}')
async def main1(ShareKey: str):

    if len(ShareKey) != 10:
        return '参数错误！'

    cache = await redis.get("123pan" + f"{ShareKey}")
    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    else:
        info = {'ShareKey':ShareKey}
        file_info = await get_file_info(info)
        url = await get_flie_url(file_info)
        head = url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={"Location": url,
                                         "Content-Type": "video/mp4",
                                         "Cache-Control": "no-cache",
                                         "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set("123pan" + f"{ShareKey}", url, ex=600)

@router.get('/123pan/{ShareKey}/{SharePwd}')
async def main(ShareKey: str,SharePwd: str):

    if len(SharePwd) != 4 or len(ShareKey) != 10:
        return '参数错误！'

    cache = await redis.get("123pan" + f"{ShareKey}")
    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "video/mp4",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    else:
        info = {'ShareKey':ShareKey,'SharePwd':SharePwd}
        file_info = await get_file_info(info)
        url = await get_flie_url(file_info)
        head = url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={"Location": url,
                                         "Content-Type": "video/mp4",
                                         "Cache-Control": "no-cache",
                                         "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set("123pan" + f"{ShareKey}", url, ex=600)