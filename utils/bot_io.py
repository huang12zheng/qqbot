
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