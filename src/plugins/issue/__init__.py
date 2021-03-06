
from nonebot import on_command,get_driver,on_notice,require
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment,Message
from utils.bot_io import readfile,savefile
import time

Inited:bool=False
issues={}
def Init():
    global Inited
    Inited = True
    issues = readfile(__file__,'issues.json')

def save_issues():
    savefile(__file__,'issues.json',issues)

command_issue = on_command('issue ')
command_show_issue = on_command('showissue',aliases={'si'})
command_show_my_issue = on_command('showmyissue',aliases={'smi'})
@command_issue.handle()
async def on_issue(bot: Bot, event: Event, state: dict):
    uid = str(event.user_id)
    gid = str(event.group_id)
    if not Inited:
        Init()
    # args = event.raw_message.split()[1]
    if not gid in issues:
        issues[gid]={}
    if not uid in issues[gid]:
        issues[gid][uid]={}
    issues[gid][uid]={
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) :
        event.raw_message
    }
    save_issues()
    await bot.send(event,"提交成功,感谢欧尼酱")

@command_show_issue.handle()
async def show_issue(bot: Bot, event: Event, state: dict):
    gid = str(event.group_id)
    uid = str(event.user_id)
    if not Inited:
        Init()
    msg = ''
    count=0
    if not gid in issues:
        issues[gid]={}
    if not uid in issues[gid]:
        issues[gid][uid]={}
    for user in issues[gid]:
        for timestamp in issues[gid][user]:
            count+=1
            print(issues[gid][user][timestamp])
            print(issues[gid][user][timestamp][5:])
            msg+=issues[gid][user][timestamp][6:]+'\n'
            if count==6: break
        if count==6: break
    await bot.send(event,f"欧尼酱:\n{msg}")

@command_show_my_issue.handle()
async def show_my_issue(bot: Bot, event: Event, state: dict):
    gid = str(event.group_id)
    uid = str(event.user_id)
    if not Inited:
        Init()
    msg = ''
    count=0
    # for user in issues[gid]:
    if not gid in issues:
        issues[gid]={}
    if not uid in issues[gid]:
        issues[gid][uid]={}
    for timestamp in issues[gid][uid]:
        count+=1
        msg+=issues[gid][user][timestamp][6:]+'\n'
    await bot.send(event,f"欧尼酱:\n{msg}")