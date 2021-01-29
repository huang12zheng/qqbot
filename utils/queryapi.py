import aiohttp
import asyncio

from nonebot import logger
import time
import json

apiroot = 'https://help.tencentbot.top'
# 第一次请求有了结果,但未被第二次使用的数据
check_time_dict={}
rank_dict={}

async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                if not response.status//100 == 2:
                    print(response)
                await asyncio.sleep(1)
                content = await response.read()
                return json.loads(content)
            except expression as identifier:
                print(identifier)
            
            

def isInPeriod(viewer_id: int) -> bool:
    value = check_time_dict[viewer_id] # exist by Branch statements in "getprofile"
    period = value.split()[1]

    if float(period)>time.time():
        return True
    return False

async def getprofile(viewer_id: int, interval: int = 1, full: bool = False,isCanLog=False) -> dict:

    reqid:int
    if not viewer_id in check_time_dict or not isInPeriod(viewer_id):
        response=await get(f'{apiroot}/enqueue?full={full}&target_viewer_id={viewer_id}')
        if response is None:
            if isCanLog: logger.info(f'{apiroot}/query?request_id={reqid}')
            return "id err"
        reqid = response['reqeust_id']
        # 是新请求,旧请求去掉
        if not reqid in rank_dict:
            # 通过 viewer_id 来取到旧请求
            if viewer_id in check_time_dict:
                reqid_o=check_time_dict[viewer_id].split()[0]
                if reqid_o in rank_dict: del rank_dict[reqid_o]
        check_time_dict[viewer_id] = f"{reqid} {time.time()+180}" #秒的格式 # id 过期时间

    reqid=check_time_dict[viewer_id].split()[0]
    # 请求有值
    if reqid in rank_dict: return rank_dict[reqid]
    
    if isCanLog: logger.info(f'{viewer_id}\n')
    if isCanLog: logger.info(f'{apiroot}/query?request_id={reqid}')

    while True:
        try:
            query= await get(f'{apiroot}/query?request_id={reqid}')
            
            status = query['status']
            if status == 'done':
                # 已经取到结果,第一次请求的信息无用了.
                # 但是,,,
                if viewer_id in check_time_dict: del check_time_dict[viewer_id]
                if isCanLog: logger.info(f'success')
                rank_dict[reqid]=query['data']
                return query['data']
            elif status == 'queue':
                time.sleep(interval)
            else: # notfound or else
                return "queue"
        except:
            return f"queue {reqid}"
'''
def queryarena(defs: list, page: int) -> dict:
    return json.loads(requests.get(f'{apiroot}/arena?def={",".join([str(x) for x in defs])}&page={page}').content.decode('utf8'))

print(queryarena([101001,102601,107601,102101,100701], 0))#page must under 9'''
