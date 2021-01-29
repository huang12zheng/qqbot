from nonebot import on_command,get_driver,on_notice,require
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment,Message
from os import path
from nonebot.log import logger
import json
import nonebot
import asyncio
from utils.queryapi import getprofile


import copy
import re

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.scheduler import scheduler
from utils.asyncio_handle import tasks
from utils.bot_io import readfile,savefile
from utils.nonebot_uils import commandHandle
import time

Inited = False
askwhere = {}

def Init():
    global Inited
    global askwhere
    Inited = True
    askwhere = readfile(__file__,'uid_list.json')
#################### Command Set B ####################

@commandHandle('askwhere ',aliases={'where '})
async def askwhere_fn(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    try:
        message = f'{event.message}'
        print(message)
        # args = message.split()
        name = message
        if message in askwhere:
            uid = askwhere[message]
            
            res = await getprofile(uid,isCanLog=True)
            res = res["user_info"]
            strList = []
            strList.append("\n")
            strList.append("竞技场排名：")
            strList.append(str(res["arena_rank"]))
            strList.append("\n")
            strList.append("公主竞技场排名：")
            strList.append(str(res["grand_arena_rank"]))
            await bot.send(event,"".join(strList),at_sender=True)

        else:
            await bot.send(event,"困惑の中!(それを知らない)",at_sender=True)
    except Exception as e:
        await bot.send(event,"困惑の中!",at_sender=True)
        raise e


@commandHandle('whereadd ')
async def add(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    
    message = f'{event.message}'
    args = message.split()
    if not len(args) ==2:
        await bot.send(event,"参数个数错误，请检查",at_sender=True)
        return
    
    username = args[0]
    id = args[1]
    if not id.isdigit() or not len(id) == 13:
        await bot.send(event,"ID格式错误，请检查",at_sender=True)
        return
    
    askwhere[username]=id
    save_askwhere()
    await bot.send(event,"谢谢,欧尼酱!",at_sender=True)

def save_askwhere():
    savefile(__file__,'uid_list.json',askwhere)