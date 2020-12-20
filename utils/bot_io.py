
'''
-*- coding: utf-8 -*-
@Author  : HZ
@File    : bot_io.py
ref: https://www.cnblogs.com/shoufengwei/p/7606084.html
'''
# from redis.client import Redis
from redis.client import Redis
from nonebot.matcher import Matcher

# Matcher.sendWithDb=
# def getInt(self,key: str):
#     value = self.get(key)
#     return 0 if value is None else int(value)

# async def sendlock(self,r,key,value,func=lambda v: str(v) ): 
#     await self.send(func(value))
#     r.set(key,value)

# Redis.getInt = getInt
# Matcher.sendlock = sendlock
def getInt(r: Redis,key: str):
    value = r.get(key)
    return 0 if value is None else int(value)

async def sendlock(m:Matcher, r:Redis,key:str,value,func=lambda v: str(v) ): 
    await m.send(func(value))
    r.set(key,value)

def merge(keylen,l1,l2,func=lambda a,b: a+b):
    return [ func(l1[id],l2[id]) for id in range(keylen) ]
def curMset():pass
def mergeBykeys(r:Redis,detaKeys:[str],detaValue,func=lambda a,b: a+b): 
    # oldValue = [ 0 if value is None else int(value) for value in r.mget(detaKeys)]
    oldValue = getNoNone(r.mget(detaKeys))
    return merge(len(detaKeys),oldValue,detaValue,func)
def mergeByGenfun(r:Redis,keys:[str],genfunc,detaValue,func=lambda a,b: a+b): 
    detaKeys=[ genfunc(key) for key in keys ]
    return mergeBykeys(r,detaKeys,detaValue,func)
def findIdWhere(l,func):
    _l=getNoNone(l)
    # if (len(l)>0):
    #     return _l.index(func(_l))
    # else:
    #     return
    return None if (len(l)==0) else _l.index(func(_l))
def getNoNone(l,func=int):
    return [ 0 if value is None else func(value) for value in l]