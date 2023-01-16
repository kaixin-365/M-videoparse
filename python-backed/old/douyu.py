import execjs
import httpx
import asyncio
from time import time
from json import loads
from hashlib import md5
from re import findall

# from router.router import router
# from services.redis import *
# from fastapi import Response

client = httpx.AsyncClient()

async def get_sign(vid: str):
    url = 'https://v.douyu.com/show/getData'
    params = {
        'vid': vid
    }
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'cache-control': 'no-cache',
        'Connection': 'keep-alive',
        'referer': f'https://v.douyu.com/show/{vid}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    json = await client.get(url=url, params=params, headers=headers)
    json = json.json()['data']
    # 拼接待执行解密JS
    raw_js = json['reqsign']['encoderJS'] + json['reqsign']['decoderJS']
    raw_js = raw_js.split('eval(strc)')[0] + 'strc};'
    # 获取解密后的JS
    node = execjs.get()
    raw_js_context = node.compile(raw_js)
    raw_js_context = raw_js_context.eval('ub98484234()')
    # 获取解密后的JS需要的参数
    point_id = str(json['videoInfo']['point_id'])
    global did, now, ver
    did = '10000000000000000000000000001501'
    now = str(int(time()))
    ver = findall('[0-9]+',str(json['reqsign']['vert']).split('=')[1])[0]
    get_sign_need = point_id + did + now + ver
    # 处理解密后的JS
    make_js = str(raw_js_context).split('var rb=CryptoJS.MD5(cb).toString();')
    md5_str = md5(get_sign_need.encode('UTF-8')).hexdigest()
    js = 'function getpath(){var rb=' + f'\"{md5_str}\";{make_js[1]}'.split(');;;;')[0]
    js = js.split(str(findall('var rt.*re;',js)[0]))[0] + 'return re;}'
    # 获取sign
    decode_js_context = node.compile(js)
    sign = str(decode_js_context.eval('getpath()'))
    return sign

async def get_url(vid: str):
    sign = await get_sign(vid)
    stream_url = 'https://v.douyu.com/api/stream/getStreamUrl'
    data = f'v={ver}&did={did}&tt={now}&sign={sign}&vid={vid}'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'cache-control': 'no-cache',
        'content-length': '124',
        'content-type': 'application/x-www-form-urlencoded',
        # 取1080p60fps super流需要这个cookie
        'cookie': 'acf_auth=d217Z4l3mmlOZ6PGGFVsFHpSTNXOAgpUOHNyIFgqU%2BaqFyTL4hjn6g9gXdNbT4osrigHMMDSejZuISEztjO0NloTi5qXVrgH9C%2Fz%2BRE7bbUMKKHPBWLB;',
        'referer': f'https://v.douyu.com/show/{vid}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    stream_json = await client.post(stream_url, data=data, headers=headers)
    stream_json = stream_json.json()['data']['thumb_video']
    return stream_json
print(asyncio.run(get_url('aRbBv3PlQdg76PYV')))