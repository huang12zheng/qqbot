from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event

remind = on_command("jc", rule=to_me(),aliased=["记恨","记仇","jh"])

@remind.handle()
async def handle_first_receive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["who"] = args  # 如果用户发送了参数则直接赋值

@remind.got("who", prompt="你想标记谁?")
async def handle(bot: Bot, event: Event, state: dict):
    who = state["who"]
    await weather.finish(who)