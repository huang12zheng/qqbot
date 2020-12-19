from nonebot import on_command,get_driver
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event
from redis.client import Redis
from redis.connection import ConnectionPool

import utils.bot_io as botIO

# port:int = Bot.
driver = get_driver()
pool = ConnectionPool(host='host.docker.internal', port=driver.config.redis_port, decode_responses=True)
r = Redis(host='host.docker.internal', port=driver.config.redis_port, decode_responses=True)

mark = on_command("jc", aliases={"记恨","标记","记仇","jh","bj"})
search=on_command("search", aliases={"查询","查找"})

class BJ:
    victim:str
    # assassin:str
    assassins:[str]
    victimValue:int
    # assassinValue:int
    assassinValues:[int]
    r:Redis

    def __init__(self,victim,assassinsStr,r:Redis):
        self.victim=str(victim)
        # self.assassin=str(assassinsStr)
        self.assassins = str.split(assassinsStr)
        self.r = r
        # victim受伤次数+=伤害者数 # 同名重复
        self.victimValue = botIO.getInt(r,f"victimCount:{self.victim}")+len(self.assassins)
        assassinsKey:[str] = [ f"assassinCount:{assassin}" for assassin in self.assassins ]
        # assassin伤害他人次数
        self.assassinValues = [ 1 if value is None else int(value)+1 for value in r.mget(assassinsKey)]
        # for assassin in assassins:
        #   assassinValues[assassin] = botIO.getInt(r,f"assassin:{assassin}")+1
        
        print("successed")
    def save(self):
        r.set("victimCount:"  +self.victim,   self.victimValue)
        r.mset(dict(
            zip(
                [ f"assassinCount:{assassin}" for assassin in self.assassins ],
                self.assassinValues
            ))
        )
        r.sadd(f"assassins:{self.victim}",*set(self.assassins))
        
        # r.sadd(f"victims:{self.assassin}",self.victim) 
        for assassin in self.assassins:
            r.sadd(f"victims:{assassin}", self.victim)



@mark.handle()
async def handle_mark(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["BJ"] = BJ(event.user_id,event.plain_text,r)

@mark.got("BJ", prompt="你想标记谁?")
async def handle_got_bj(bot: Bot, event: Event, state: dict):

    bj:BJ = state["BJ"]
    # mes:str = f"{bj.assassin}的被标记次数:{bj.assassinValue}"
    ids = [ id for id in range(len(bj.assassins))]
    mes:str = '\n'.join([
        f"{bj.assassins[id]}的被标记次数:{bj.assassinValues[id]}" for 
            id in range(len(bj.assassins))
        ])
    await bot.send(event,mes)
    bj.save()
    await handle_search(bot,event,state)


@search.handle()
async def handle_search(bot: Bot, event: Event, state: dict):
    who:str = str(event.user_id)
    victimValue=r.get("victimCount:"+who)
    assassins=r.smembers("assassins:"+who)
    doValue=r.get("assassinCount:"+who)

    mes:str = f"{who}的情况是:\n受到伤害次数:{victimValue} \n伤害者: {assassins}\n被标记次数: {doValue}"
    await bot.send(event,mes)