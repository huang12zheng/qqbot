from nonebot import on_command,get_driver
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event
from redis.client import Redis
from redis.connection import ConnectionPool

import utils.bot_io as botIO
import random
import datetime
from collections import Counter

# port:int = Bot.
driver = get_driver()
pool = ConnectionPool(host='host.docker.internal', port=driver.config.redis_port, decode_responses=True)
r = Redis(host='host.docker.internal', port=driver.config.redis_port, decode_responses=True)

mark = on_command("jc", aliases={"记恨","标记","记仇","jh","bj"})
search=on_command("search", aliases={"查询","查找","s"})
sw=on_command("sw", aliases={"swho"})
mergeByGenfun=botIO.mergeByGenfun
class BJ:
    r:Redis
    # 受害者
    victim:str
    # 伤害者们
    assassins:[str]
    # 本人受害数
    victimValue:int
    # 伤害者们的伤害数,
    # "assassinValue:{assassin}"为单个伤害者的伤害数
    assassinValues:[int]
    # 伤害者们对victim的伤害数
    assassinVictimValues:[int]
    # 当日本人受害数
    curVictimValue:int
    # 当日伤害者们的伤害数
    # "curAssassinValue:{date}:{assassin}"
    curAssassinValues:[int]
    # 当日伤害者们的伤害victim数
    # "curAssassinVictimValue:{date}:{self.victim}:{assassin}"
    curAssassinVictimValues:[int]
    isBJCountGt5:bool

    def __init__(self,victim,assassinsStr,r:Redis):
        self.r = r
        
        self.victim=str(victim)
        date:str = datetime.datetime.now().strftime('%y%m%d')

        
        _assassins = str.split(assassinsStr) #伤害者列表
        assassinCount = Counter(_assassins) # xx.value is detaValue
        self.assassins = list(assassinCount)
        count = assassinCount.most_common(1)[0][1]
        if count>5:
            self.isBJCountGt5=True
            return
        else:
            self.isBJCountGt5=False

        # victim受伤次数+=伤害者数 # 同名重复
        self.victimValue = botIO.getInt(r,f"victimValue:{self.victim}")+len(_assassins)
        
        self.curVictimValue=botIO.getInt(r,f"curVictimValue:{date}:{self.victim}")+len(_assassins)
        
        # assassin伤害他人次数
        self.assassinValues = mergeByGenfun(r,
            self.assassins, #detaKeysFrom #assassinCount.keys
            lambda assassin: f"assassinValue:{assassin}",
            list(assassinCount.values()) #detaValue # assassinCount.values
        )

        self.assassinVictimValues = mergeByGenfun(r,
            self.assassins, #detaKeysFrom
            lambda assassin: f"assassinVictimValue:{self.victim}:{assassin}",
            list(assassinCount.values()) # #detaValue
        )
        
        # 当日assassins伤害victim次数
        self.curAssassinVictimValues = mergeByGenfun(r,
            self.assassins, #detaKeysFrom
            lambda assassin: f"curAssassinVictimValue:{date}:{self.victim}:{assassin}",
            list(assassinCount.values()) # #detaValue
        )
        
        # 当日assassins伤害他人次数
        self.curAssassinValues = mergeByGenfun(r,
            self.assassins, #detaKeysFrom
            lambda assassin: f"curAssassinValue:{date}:{assassin}",
            list(assassinCount.values()) # #detaValue
        )
        
        print("successed")
    def save(self):
        # 日期
        date:str = datetime.datetime.now().strftime('%y%m%d')
        r.sadd(f"assassins:{self.victim}",*set(self.assassins))
        r.set(f"victimValue:"  +self.victim,   self.victimValue)
        r.set(f"curVictimValue:{date}:"+self.victim,   self.curVictimValue)
        
        r.mset(dict(
            zip(
                [ f"assassinValue:{assassin}" for assassin in self.assassins ],
                self.assassinValues
            ))
        )
        r.mset(dict(
            zip(
                [ f"curAssassinValue:{date}:{assassin}" for assassin in self.assassins ],
                self.curAssassinValues
            ))
        )

        r.mset(dict(
            zip(
                [ f"assassinVictimValue:{self.victim}:{assassin}" for assassin in self.assassins ],
                self.assassinVictimValues
            ))
        )

        r.mset(dict(
            zip(
                [ f"curAssassinVictimValue:{date}:{self.victim}:{assassin}" for assassin in self.assassins ],
                self.curAssassinVictimValues
            ))
        )
        
        # assassin 的受害者们是
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
    if bj.isBJCountGt5 :
        await bot.send(event,"标记个数过多") # TODO
    else:
        ids = [ id for id in range(len(bj.assassins))]
        mes:str = '\n'.join([
            f"{bj.assassins[id]}的被标记次数:{bj.assassinValues[id]}" for 
                id in range(len(bj.assassins))
            ])
        await bot.send(event,mes)
        bj.save()
        flag = random.random() 
        if flag > 0.87: await handle_search(bot,event,state) 


@search.handle()
async def handle_search(bot: Bot, event: Event, state: dict):
    date:str = datetime.datetime.now().strftime('%y%m%d')
    who:str = str(event.user_id)

    victimValue=r.get("victimValue:"+who)
    _assassins=r.smembers("assassins:"+who)
    assassins=list(_assassins)
    doValue=r.get("assassinValue:"+who)
    curAssassinValue=r.get(f"curAssassinValue:{date}:{who}")
    curMostAssassinId=botIO.findIdWhere(
        r.mget([ f"curAssassinVictimValue:{date}:{who}:{assassin}" for assassin in assassins]),
        max
    )
    mostAssassinId=botIO.findIdWhere(
        r.mget([ f"assassinVictimValue:{who}:{assassin}" for assassin in assassins]),
        max
    )
    
    curMostAssassin=""

    mes:str = f"""{who}的情况是:
        受到伤害次数:{victimValue}
        伤害者: {assassins}
        被标记次数: {doValue}
        当日被标记次数: {curAssassinValue}
        谁最伤害你:{None if mostAssassinId == None else assassins[mostAssassinId]}
        你当日的最大标记者是:{None if curMostAssassinId == None else assassins[curMostAssassinId]}
    """
    await bot.send(event,mes)
@sw.handle()
async def handle_sw(bot: Bot, event: Event, state: dict):
    argsStr = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if argsStr:
        args = argsStr.split()
        if len(args)>1 :
            await bot.send(event,"参数过多")
        elif len(args)==0:
            # await bot.send(event,"参数过多")
            await handle_search(bot,event,state)
        else:
            victim = argsStr
            date:str = datetime.datetime.now().strftime('%y%m%d')
            curVictimValue=botIO.getInt(r,f"curVictimValue:{date}:{victim}")
            curAssassinValue=r.get(f"curAssassinValue:{date}:{victim}")
            mes:str = f"""{victim}
            当日被伤害次数:{curVictimValue}
            当日被标记次数: {curAssassinValue}
            """
            await bot.send(event,mes)
            # 当日被标记次数: {curAssassinValue}\n
        # state["BJ"] = BJ(event.user_id,event.plain_text,r)


# def checkBJCount(maxCount:int=5):
