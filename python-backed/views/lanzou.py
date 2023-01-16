from re import findall
from httpx import AsyncClient
from router.router import router
from services.redis import redis
from fastapi import Response

headers = {
    'accept': 'text/html,*/*',
    'accept-encoding': 'gzip',
    'accept-language': 'zh-CN,zh;q=0.8,en;q=0.8',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
}

html_url = 'https://m.lanzoux.com/tp/'
post_url = 'https://m.lanzoux.com/ajaxm.php'

client = AsyncClient()

async def get_sign(fileid: str):
    try:
        html = await client.get(url = html_url + fileid, headers=headers)
        html = html.text
    except:
        return '(X_X) 服务器获取sign出错'
    postsign = str(findall('\'.*_c_c', html)[0]).split('\'')[1]
    print(postsign)
    return postsign

async def get_url(sign: str, fileid: str,password:str):
    post_headers = {
    'Accept': 'application/json,*/*',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.8',
    'Referer': f'https://m.lanzoux.com/tp/{fileid}',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    }
    post_data = {'action': 'downprocess', 'sign': sign, 'p': password}
    try:
        req = await client.post(url=post_url, headers=post_headers, data=post_data)
        req = req.json()
        url = req['dom'] + '/file/' + req['url']
    except:
        return '(X_X) 服务器获取链接出错'
    real_url = await client.get(url=url, headers=headers)
    real_url = str(real_url.headers['Location']).split('&b=')[0]
    return real_url

async def get_nopass_url(fileid: str):
    try:
        html = await client.get(url = html_url + fileid, headers=headers)
        html = html.text
    except:
        return '(X_X) 服务器获取链接出错'
    url_pass = str(findall("\?.*'", html)[0]).split('\'')[0]
    url = f'https://developer.lanzoug.com/file/{url_pass}'
    real_url = await client.get(url = url, headers=headers)
    real_url = str(real_url.headers['Location']).split('&b=')[0]
    return real_url

@router.get('/lanzou/{fileid}')
async def no_pass_main(fileid: str):
    cache = await redis.get(f"lanzou{fileid}")
    if cache is not None:
        return Response(status_code=307,
                headers={"Location": cache,
                         "Content-Type": "application/octet-stream",
                         "Cache-Control": "no-cache",
                         "X-Cache-used": "Yes",
                         "Referrer-Policy": "no-referrer"})
    
    if cache is None:
        url = await get_nopass_url(fileid)
        try:
            return Response(status_code=307,
                headers={"Location": url,
                         "Content-Type": "application/octet-stream",
                         "Cache-Control": "no-cache",
                         "X-Cache-used": "Yes",
                         "Referrer-Policy": "no-referrer"})
        finally:
            await redis.set(f"lanzou{fileid}", url ,ex=600)

@router.get('/lanzou/{fileid}/{password}')
async def main(fileid:str, password:str):
    cache = await redis.get(f"lanzou{fileid}")
    if cache is not None:
        return Response(status_code=307,
                        headers={"Location": cache,
                                 "Content-Type": "application/octet-stream",
                                 "Cache-Control": "no-cache",
                                 "X-Cache-used": "Yes",
                                 "Referrer-Policy": "no-referrer"})
    
    if cache is None:
        try:
            sign = await get_sign(fileid)
            url = await get_url(sign, fileid, password)
        except:
            pass
        head = url[0:8]
        if head == 'https://':
            try:
                return Response(status_code=307,
                                headers={"Location": url,
                                        "Content-Type": "video/mp4",
                                        "Cache-Control": "no-cache",
                                        "Referrer-Policy": "no-referrer"})
            finally:
                await redis.set(f"lanzou{fileid}", url, ex=600)



