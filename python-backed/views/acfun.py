from json import loads
from re import match,I
from lxml import etree
from httpx import AsyncClient
from router.router import router
from services.redis import redis,ac_bangumi_redis
from fastapi import Response, Query

# 创建HTTP长连接池
client = AsyncClient(http2=True,verify=False)

parms = {
    'quickViewId' : 'videoInfo_new',
    'ajaxpipe':'1',
    #'reqID':'2'
    #'t':'当前UNIX时间'
}

plist_parms = {
    'pagelets' : 'pagelet_partlist',
    'ajaxpipe':'1',
    #'reqID':'0'
    #'t':'当前UNIX时间'
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'cache-control': 'no-cache',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

async def get_video_link(vid: str):
    try:
        html_doc = await client.get(url = f'https://www.acfun.cn/v/{vid}',params=parms,headers = headers,timeout=8)
        html_doc = html_doc.text.split('/*<!-- f')[0]
    except:
        return '服务器获取信息出错！可能视频不存在！'
    try:
        html_doc1 = str(loads(html_doc)['html']).split('= window.videoInfo =')[1]
        KS_json = loads(html_doc1.split('</script>')[0])['currentVideoInfo']['ksPlayJson']
        url_json = loads(KS_json)['adaptationSet'][0]['representation']
    except:
        return '获取链接过程出错！'

    return url_json

async def get_bangumi_link(vid: str,p: int):
    if p >= 2:
        plist_cache = await ac_bangumi_redis.hget("acfun_bgm" + f"{vid}" + 'plist', p)
        if plist_cache is None:
            try:
                plist_html = await client.get(url = f'https://www.acfun.cn/bangumi/{vid}',params=plist_parms,headers = headers,timeout=8)
                plist_html = plist_html.text.split('/*<!-- f')[0]
                plist_html = loads(plist_html)['html']
                plist_html = etree.HTML(plist_html)
            except:
                return '服务器获取番剧分P信息出错！'
            try:
                alist = plist_html.xpath('//li[@class="single-p"]')
                url_path = alist[p-2].values()[2]
                html_doc = await client.get(url = f'https://www.acfun.cn{url_path}',params=parms,headers = headers,timeout=8)
                html_doc = html_doc.text.split('/*<!-- f')[0]
            except:
                return '服务器获取番剧分P信息超时！'
            finally:
                p_list_p = []
                p_list_urlpath = []
                for k in range(2,len(alist)+2):
                    p_list_p.append(k)
                for i in alist:
                    p_list_urlpath.append(i.values()[2])
                p_list=dict(zip(p_list_p,p_list_urlpath))

                await ac_bangumi_redis.hset("acfun_bgm" + f"{vid}" + 'plist', mapping = p_list) 

        if plist_cache is not None:
            try:
                html_doc = await client.get(url = f'https://www.acfun.cn{plist_cache}',params=parms,headers = headers,timeout=8)
                html_doc = html_doc.text.split('/*<!-- f')[0]
            except:
                return '服务器缓存信息出错！'

    if p == 1:
        try:
            html_doc = await client.get(url = f'https://www.acfun.cn/bangumi/{vid}',params=parms,headers = headers,timeout=8)
            html_doc = html_doc.text.split('/*<!-- f')[0]
        except:
            return '服务器获取信息出错！可能番剧不存在或者需要付费！'
    
    try:
        html_doc1 = str(loads(html_doc)['html']).split('= window.bangumiData =')[1]
        KS_json = loads(html_doc1.split('</script>')[0])['currentVideoInfo']['ksPlayJson']
        url_json = loads(KS_json)['adaptationSet'][0]['representation']
    except:
        return '获取链接过程出错！'
    return url_json

async def retrun_links(json: list,is4k: bool,isJson: bool):
    url_dict = {}
    qualitys = ['1080p60','1080p+','1080p','720p60','720p','540p','360p']
    for k in range(len(json)):
        vjson = json[k]
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
async def main(vid: str, q: str = Query("1080p", min_length=2, max_length=5), p: int = 1):
    match_ac = match(r'ac[0-9]+', vid, I)
    match_aa = match(r'aa[0-9]+', vid, I)
    if match_ac is None and match_aa is None:
        return '视频号输入错误！'
    if match_ac and match_aa:
        return '非法参数！'

    if match_ac:
        del p
        cache = await redis.get("acfun" + f"{vid}" + '?q=' + q)

    if match_aa:
        cache = await redis.get("acfun_bgm" + f"{vid}" + '?q=' + q +'&p=' + str(p))

    while cache is not None:
        return Response(status_code=307,
                headers={
                    "Location": cache,
                    "Content-Type": "application/vnd.apple.mpegurl",
                    "Cache-Control": "no-cache",
                    "Referrer-Policy": "no-referrer",
                    "X-Cache-used": "Yes"})

    while cache is None and match_ac is not None:
        ac_json = await get_video_link(vid)
        if q == '1080p':
            url = await retrun_links(ac_json,False,False)

        if q == '4k':
            url = await retrun_links(ac_json,True,False)

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

    while cache is None and match_aa is not None:
        aa_json = await get_bangumi_link(vid,p)

        if q == '1080p':
            url = await retrun_links(aa_json,False,False)

        if q == '4k':
            url = await retrun_links(aa_json,True,False)

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
                # await redis.set("acfun_bgm" + f"{vid}" + '?q=' + q +'&p=' + str(p), url, ex=600)
                pass
        else:
            return url