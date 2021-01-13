#Created by ColdThunder11 2021/1/3
#changed by lulu to another api 2021/1/7
#changed by hz to another api 2021/1/11
from nonebot import on_command,get_driver,on_notice,require
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment,Message
from os import path
from nonebot.log import logger
import json
import nonebot
import asyncio
from .queryapi import getprofile
import copy
import re

##############################
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment,Message
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import time

sv_help = '''
[竞技场绑定 uid] 绑定竞技场排名变动推送（仅下降），默认双场均启用
[竞技场查询( uid)] 查询竞技场简要信息
[停止竞技场订阅] 停止战斗竞技场排名变动推送
[停止公主竞技场订阅] 停止公主竞技场排名变动推送
[启用竞技场订阅] 启用战斗竞技场排名变动推送
[启用公主竞技场订阅] 启用公主竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
'''.strip()

# scheduler = require('nonebot_plugin_apscheduler')
# ascheduler = require('nonebot_plugin_apscheduler').scheduler

# sv = Service('竞技场推送',help_=sv_help, bundle='pcr查询')
# sv = nonebot

Inited = False
pcrprofile = None
binds = {}
arena_ranks = {}
grand_arena_ranks ={}
tr = None

jjchelp = on_command('jjc帮助')
arena_bind=on_command('竞技场绑定',aliases={'jjcbind','bind','b'})
query_arena=on_command('竞技场查询',aliases={'js','jjcsearch'})
disable_arena_sub=on_command('停止竞技场订阅')
disable_grand_arena_sub=on_command('停止公主竞技场订阅')
enable_arena_sub=on_command('启用竞技场订阅')
enable_grand_arena_sub=on_command('启用公主竞技场订阅')
delete_arena_sub=on_command('删除竞技场订阅',aliases={'unbind'})
send_arena_sub_status=on_command('竞技场订阅状态')
switch_bind=on_command('switch')


@jjchelp.handle()
async def send_jjchelp(bot: Bot, event: Event, state: dict):
    await bot.send(event, sv_help)

def Init():
    global Inited
    global pcrprofile
    global binds
    global tr
    Inited = True
    config_path = path.join(path.dirname(__file__),"binds.json")
    with open(config_path,"r",encoding="utf8")as fp:
        binds = json.load(fp)

def save_binds():
    config_path = path.join(path.dirname(__file__),"binds.json")
    jsonStr = json.dumps(binds, indent=4)
    with open(config_path,"r+",encoding="utf8")as fp:
        fp.truncate(0)
        fp.seek(0)
        fp.write(jsonStr)

isCanBind:bool = True
@switch_bind.handle()
async def on_switch_bind(bot: Bot, event: Event, state: dict):
    global isCanBind
    isCanBind = not isCanBind
    await bot.send(event,f"bindState is {isCanBind}")

@arena_bind.handle()
async def on_arena_bind(bot: Bot, event: Event, state: dict):
    global binds
    if not isCanBind:
        await bot.send(event,"暂不支持bind")
        return

    if not Inited:
        Init()
    id = f'{event.message}'
    if not id.isdigit() or not len(id) == 13:
        await bot.send(event,"ID格式错误，请检查",at_sender=True)
        return
    uid = str(event.user_id)
    gid = str(event.group_id)
    if not uid in binds["arena_bind"]:
        binds["arena_bind"][uid] = {"id":id,"uid":uid,"gid":gid,"arena_on":True,"grand_arena_on":True}
    else:
        binds["arena_bind"][uid]["id"] = id
        binds["arena_bind"][uid]["uid"] = uid
        binds["arena_bind"][uid]["gid"] = gid
    save_binds()
    await bot.send(event,"竞技场绑定成功",at_sender=True)

@query_arena.handle()
async def on_query_arena(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
        return
    else:
        id = binds["arena_bind"][uid]["id"]
    if not id.isdigit() or not len(id) == 13:
        await bot.send(event,"ID格式错误，请检查",at_sender=True)
        return
    try:
        res = getprofile(int(id))
        res = res["user_info"]
        if res == "queue":
            logger.info("成功添加至队列"),
            await bot.send(event,"请等待源站更新数据，稍等几分钟再来查询",at_sender=True)
        if res == "id err":
            logger.info("该viewer_id有误")
            await bot.send(event,"查询出错，请检查ID是否正确",at_sender=True)
            return
        strList = []
        strList.append("\n")
        strList.append("竞技场排名：")
        strList.append(str(res["arena_rank"]))
        strList.append("\n")
        strList.append("公主竞技场排名：")
        strList.append(str(res["grand_arena_rank"]))
        await bot.send(event,"".join(strList),at_sender=True)
    except:
        await bot.send(event,"查询出错，请检查ID是否正确",at_sender=True)
    pass

@disable_arena_sub.handle()
async def disable_arena_sub(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["arena_on"] = False
        save_binds()
        await bot.send(event,"停止竞技场订阅成功",at_sender=True)

@disable_grand_arena_sub.handle()
async def disable_grand_arena_sub(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["grand_arena_on"] = False
        save_binds()
        await bot.send(event,"停止公主竞技场订阅成功",at_sender=True)

@enable_arena_sub.handle()
async def enable_arena_sub(bot,event,state):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["arena_on"] = True
        save_binds()
        await bot.send(event,"启用竞技场订阅成功",at_sender=True)

@enable_grand_arena_sub.handle()
async def enable_grand_arena_sub(bot,event,state):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["grand_arena_on"] = True
        save_binds()
        await bot.send(event,"启用公主竞技场订阅成功",at_sender=True)

@delete_arena_sub.handle()
async def delete_arena_sub(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    if len(event.message) == 1 and event.message[0].type == 'text' and not event.message[0].data['text']:
        uid = str(event.user_id)
        if not uid in binds["arena_bind"]:
            await bot.finish(event, "您还未绑定竞技场", at_sender=True)
        else:
            binds["arena_bind"].pop(uid)
            save_binds()
            await bot.send(event, "删除竞技场订阅成功", at_sender=True)
    elif event.message[0].type == 'at':
        if not priv.check_priv(event, priv.SUPERUSER):
            await bot.finish(event, '删除他人订阅请联系维护', at_sender=True)
        else:
            uid = str(event.message[0].data['qq'])
            if not uid in binds["arena_bind"]:
                await bot.finish(event, "对方尚未绑定竞技场", at_sender=True)
            else:
                binds["arena_bind"].pop(uid)
                save_binds()
                await bot.send(event, "删除竞技场订阅成功", at_sender=True)
    else:
        await bot.finish(event, '参数格式错误, 请重试')

@send_arena_sub_status.handle()
async def send_arena_sub_status(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        await bot.send(event,"您还未绑定竞技场",at_sender=True)
    else:
        strList = []
        strList.append("当前竞技场绑定ID：")
        strList.append(str(binds["arena_bind"][uid]["id"]))
        strList.append("\n竞技场订阅：")
        if binds["arena_bind"][uid]["arena_on"]:
            strList.append("开启")
        else:
            strList.append("关闭")
        strList.append("\n公主竞技场订阅：")
        if binds["arena_bind"][uid]["grand_arena_on"]:
            strList.append("开启")
        else:
            strList.append("关闭")
        await bot.send(event,"".join(strList),at_sender=True)


async def _leave(bot: Bot, event: Event, state: dict)->bool:
    if event.notice_type=='group_decrease' and event.sub_type=='leave':
        return True
    else:
        return False

leave=on_notice(_leave)
@leave.handle()
async def leave_notice(bot,event):
    if not Inited:
        Init()
    uid = str(event.user_id)
    if not uid in binds["arena_bind"]:
        pass
    else:
        binds["arena_bind"].pop(uid)
        save_binds()
        pass
    return



##################################################

def on_arena_schedule():
    global arena_ranks
    global grand_arena_ranks
    # bot = nonebot.get_bot()
    bots = driver.bots.values()
    bot:Bot
    
    try:
        if len(driver.bots) == 1:
            bot = list(bots)[0]
        else:
            return
    except:
        return 

    logger.opt(colors=True).info("<g>start schedule</g>")
    if not Inited:
        Init()
    arena_bind = copy.deepcopy(binds["arena_bind"])
    for user in arena_bind:
        user = str(user)
        if binds["arena_bind"][user]["arena_on"] or binds["arena_bind"][user]["grand_arena_on"]:
            asyncio.run(check_arena_state(bot,user))
        else:
            if user in arena_ranks: del arena_ranks[user]
            if user in grand_arena_ranks: del grand_arena_ranks[user]
    logger.opt(colors=True).info("<r>-----------------------------------------------------</r>")

async def check_arena_state(bot,user):
    try:
        gid = int(binds["arena_bind"][user]["gid"])
        uid = int(user)
        # await bot.send_msg(message_type="group",group_id=gid,user_id=uid,
        #     message=f"Test Scheduler Success {uid} {gid}"
        # )
        res = getprofile(int(binds["arena_bind"][user]["id"]))
        if type(res) is str and  res.startswith('queue'):
            logger.info(f"{res}成功添加至队列")
            return
        res = res["user_info"]
        if binds["arena_bind"][user]["arena_on"]:
            if not user in arena_ranks:
                arena_ranks[user] = res["arena_rank"]
            else:
                origin_rank = arena_ranks[user]
                new_rank = res["arena_rank"]
                if origin_rank >= new_rank:#不动或者上升
                    arena_ranks[user] = new_rank
                else:
                    msg = "[CQ:at,qq={uid}]您的竞技场排名发生变化：{origin_rank}->{new_rank}".format(uid=binds["arena_bind"][user]["uid"], origin_rank=str(origin_rank), new_rank=str(new_rank))
                    arena_ranks[user] = new_rank
        
                    logger.opt(colors=True).info(f"{msg}")
                    
                    await bot.send_msg(
                        message_type="group",
                        group_id=gid,
                        user_id=uid,
                        message=msg
                    )

                # await asyncio.sleep(1.5)
        if binds["arena_bind"][user]["grand_arena_on"]:
            if not user in grand_arena_ranks:
                grand_arena_ranks[user] = res["grand_arena_rank"]
            else:
                origin_rank = grand_arena_ranks[user]
                new_rank = res["grand_arena_rank"]
                if origin_rank >= new_rank:#不动或者上升
                    grand_arena_ranks[user] = new_rank
                else:
                    msg = "[CQ:at,qq={uid}]您的公主竞技场排名发生变化：{origin_rank}->{new_rank}".format(uid=binds["arena_bind"][user]["uid"], origin_rank=str(origin_rank), new_rank=str(new_rank))
                    grand_arena_ranks[user] = new_rank
                    
                    await bot.send_msg(
                        message_type="group",
                        group_id=gid,
                        user_id=uid,
                        message=msg
                    )

    except Exception as inst:
        logger.info("对{id}的检查出错".format(id=binds["arena_bind"][user]["id"]))
        print(inst)


# CQHTTP 2975265878 | [notice.group_decrease.leave]: {
#     'time': 1610467161, 'self_id': 2975265878, 
#     'post_type': 'notice', 'notice_type': 'group_decrease', 
#     'sub_type': 'leave', 'user_id': 805104533, 
#     'group_id': 789276860, 'operator_id': 805104533
# }
# scheduler.start()


scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
# scheduler = Bl
driver = nonebot.get_driver()

def _start_scheduler():
    if not Inited:
        Init()
    if not scheduler.running:
        scheduler.add_job(on_arena_schedule,'interval',minutes=3)
        # scheduler.add_job(on_arena_schedule,'interval',seconds=driver.config.jjcinterval)
        
        scheduler.start()
        logger.opt(colors=True).info("<y>Scheduler Started</y>")

driver.on_startup(_start_scheduler)
