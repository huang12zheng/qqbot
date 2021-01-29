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


#################### Command Set B ####################
noticehelp = on_command('notice帮助',aliases={'订阅帮助',"通知帮助","nh"})
add_sub=on_command('通知订阅',aliases={'noticebind','nb '})
delete_sub=on_command('停止通知订阅',aliases={'unnoticebind','unb '})
sub_status=on_command('订阅状态',aliases={'通知状态','ns'})
notice_config_reload=on_command('通知配置重载',aliases={"notice_reload","nr "})
switch_bind=on_command('notice_switch')
switch_log=on_command('sl_notice')
#################### Command Set E ####################
#################### Init Begin ####################
Inited = False
notices = {}
arena_ranks_bynotice = {}
grand_arena_ranks_bynotice ={}
isCanNoticeBind:bool = True
isCanLog:bool = False
driver = nonebot.get_driver()
sv_help = '''
[通知订阅 人名 uid] 绑定竞技场排名变动推送，默认双场均启用
[停止通知订阅 uid] 停止战斗竞技场排名变动推送
[订阅状态] 查看排名变动推送绑定状态
[通知配置重载]
'''.strip()

@notice_config_reload.handle() # ~~因为是volumn的, 所以要重新部署,~~
async def reload(bot: Bot, event: Event, state: dict):
    Init()
    await bot.send(event, '重载结束')

def Init():
    global Inited
    global notices
    Inited = True
    notices = readfile(__file__,'notices.json')
    # config_path = path.join(path.dirname(__file__),"notices.json")
    # with open(config_path,"r",encoding="utf8")as fp:
    #     notices = json.load(fp)

@noticehelp.handle()
async def send_help(bot: Bot, event: Event, state: dict):
    await bot.send(event, sv_help)

@sub_status.handle()
async def show_statue(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    msg = '\n'
    for uid in notices[str(event.group_id)].keys():
        dataset=notices[str(event.group_id)][uid]
        msg+=f'{dataset["username"]} {uid} {dataset["arena_on"]} {dataset["grand_arena_on"]}\n'
    await bot.send(event, msg, at_sender=True)
#################### Init End ####################
#################### LOG End ####################

@switch_log.handle()
async def switch_log(bot: Bot, event: Event, state: dict):
    global isCanLog
    isCanLog = not isCanLog
    await bot.send(event,f"isCanLog is {isCanLog}")
#################### LOG End ####################

#################### Notice Set B ####################

@switch_bind.handle()
async def on_switch_bind(bot: Bot, event: Event, state: dict):
    global isCanNoticeBind
    isCanNoticeBind = not isCanNoticeBind
    await bot.send(event,f"noticeState is {isCanNoticeBind}")

def save_notices():
    savefile(__file__,'notices.json',notices)
    # config_path = path.join(path.dirname(__file__),"notices.json")
    # jsonStr = json.dumps(notices, indent=4,ensure_ascii=False)
    # with open(config_path,"r+")as fp:
    #     fp.truncate(0)
    #     fp.seek(0)
    #     fp.write(jsonStr)

@add_sub.handle()
async def on_add_sub(bot: Bot, event: Event, state: dict):
    global notices
    if not isCanNoticeBind:
        await bot.send(event,"暂不支持通知订阅")
        return

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
    # uid = str(event.user_id)
    gid = str(event.group_id)
    if not gid in notices:
        notices[gid] = {
            f"{gid}": { "username": username, "arena_on": True, "grand_arena_on": True }
        }
    else:
        # if not id in notices[gid]:
        notices[gid][id] = { "username": username, "arena_on": True, "grand_arena_on": True }
        # else:
            # notices[gid][uid]={ "username": username, "arena_on": True, "grand_arena_on": True }
            
    save_notices()
    await bot.send(event,"通知绑定成功",at_sender=True)

@delete_sub.handle()
async def on_delete_sub(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    group = str(event.group_id)
    if not group in notices:
        await bot.finish(event, "您还未设置通知订阅", at_sender=True)
        return
    else:
        if len(event.message) == 1 and event.message[0].type == 'text' and event.message[0].data['text'].isdigit():
            uid = str(event.message)
            if not uid in notices[group]:
                await bot.send(event, "您还未设置通知订阅", at_sender=True)
                return
            else:
                notices[group].pop(uid)
                save_notices()
                await bot.send(event, "删除竞技场订阅成功", at_sender=True)
        else:
            await bot.send(event, '参数格式错误, 请重试', at_sender=True)

#################### Notice Set E ####################
#################### Sub B ####################
@scheduler.scheduled_job('interval',seconds=driver.config.jjcinterval)
def on_arena_schedule():
    if scheduler.state == 2:
        print('run into a error')
        return
    
    # sleephour=int( time.strftime("%H", time.localtime()) )
    # if sleephour >0 and sleephour <= 6: 
    #     print(time.strftime("%H", time.localtime()))
    #     return
    
    for task in tasks:
        if task.cr_code.co_filename.find('notice')>0: return
    global arena_ranks_bynotice
    global grand_arena_ranks_bynotice
    bots = driver.bots.values()
    bot:Bot

    ### init ###
    if not Inited:
        Init()

    try:
        if len(driver.bots) == 1:
            bot = list(bots)[0]
        else:
            return
    except:
        return
    ### init ###
    # notices_t = copy.deepcopy(notices)
    async def tasks_prepare(notices):
        for group in notices:
            group = str(group)
            gid   = int(group)
            if not group in grand_arena_ranks_bynotice: grand_arena_ranks_bynotice[group]={}
            if not group in arena_ranks_bynotice: arena_ranks_bynotice[group]={}
            for user in notices[group]:
                user = str(user)
                if notices[group][user]["arena_on"] or notices[group][user]["grand_arena_on"]:
                    await check_arena_state(bot,group,user)
                    # await asyncio.create_task(check_arena_state(bot,group,user))  # 顺序 非 并发 以防514
                    # await asyncio.create_task(await check_arena_state(bot,group,user))  # ERROR
                else:
                    # { group:{user: rank} }
                    if user in arena_ranks_bynotice[group]: del arena_ranks_bynotice[group][user]
                    if user in grand_arena_ranks_bynotice[group]: del grand_arena_ranks_bynotice[group][user]

    tasks.append(tasks_prepare(notices))
    # asyncio.run(tasks_prepare(notices))   ### main entrance
    global isCanLog
    if isCanLog: logger.opt(colors=True).info("<r>-----------------------------------------------------</r>")
    
async def check_arena_state(bot,group,user):
    try:
        gid = int(group)
        uid = int(user)
        if isCanLog: print(f"{group}.{user}")
        res = await getprofile(uid,isCanLog=isCanLog)
        if type(res) is str and  res.startswith('queue'):
            logger.info(f"{res}成功添加至队列")
            return
        # res = res["user_info"]
        # arena_ranks_bynotice is data_set
        ## arena_ranks_bynotice key is what? 
        ## GA notice  ## GB is need to notice too

        def template_handle(template:str):
            def msg_handle(username,origin_rank,new_rank):
                return template.format(username=username,origin_rank=origin_rank,new_rank=new_rank)
            return msg_handle
                # f"{username}的竞技场排名发生变化：{origin_rank}->{new_rank}"
        if isCanLog: print("221 is running")
        task1=notice_task(
            bot,
            gid,
            on_flag=notices[group][user]["arena_on"],
            data_set=arena_ranks_bynotice[group],
            key = notices[group][user]['username'],
            value = res["user_info"]["arena_rank"],
            msg_handle=template_handle("{username} 的竞技场排名发生变化：{origin_rank}->{new_rank}")
        )

        task2=notice_task(
            bot,
            gid,
            on_flag=notices[group][user]["grand_arena_on"],
            data_set=grand_arena_ranks_bynotice[group],
            key = notices[group][user]['username'],
            value = res["user_info"]["grand_arena_rank"],
            msg_handle=template_handle("{username} 的公主竞技场排名发生变化：{origin_rank}->{new_rank}")
        )
        if isCanLog: print("231 is running")
        await asyncio.gather(
            asyncio.create_task(task1),
            asyncio.create_task(task2)
        )

    except Exception as inst:
        logger.info(f"对{group}.{user}的检查出错")
        print(inst)


#################### Sub E ####################
# on_flag
# data_set
# msg_handle
## bot.send_msg
async def notice_task(bot,gid,on_flag,data_set,key,value,msg_handle):
    if on_flag:
        if not key in data_set:
            data_set[key] = value
        else:
            origin_rank = data_set[key]
            new_rank = value
            if origin_rank == new_rank:#不动
                pass
            else:
                # msg = f"{key}的竞技场排名发生变化：{origin_rank}->{new_rank}"
                msg = msg_handle(key,origin_rank,new_rank)
                data_set[key] = new_rank
                await bot.send_msg(
                    message_type="group",
                    group_id=gid,
                    message=msg
                )

# scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
# scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
# driver = nonebot.get_driver()
# @scheduler.sch
# def start_scheduler():
#     if not Inited:
#         Init()
    # if not scheduler.running:
        # scheduler.add_job(on_arena_schedule,'interval',seconds=driver.config.jjcinterval)
        
        # scheduler.start()
        # logger.opt(colors=True).info("<y>Notice Scheduler Started</y>")

# driver.on_startup(start_scheduler)
# start_scheduler()

@commandHandle('通知排名')
async def notice_ranks(bot: Bot, event: Event, state: dict):
    await bot.send(event,f"{arena_ranks_bynotice}")
    await bot.send(event,f"{grand_arena_ranks_bynotice}")