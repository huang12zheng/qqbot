from nonebot import get_driver, export
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from nonebot.log import logger
# scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
scheduler = BackgroundScheduler(
    timezone="Asia/Shanghai",
    job_defaults = {
        # 最近多久时间内允许存在的任务数
        'misfire_grace_time': 11,
        # 该定时任务允许最大的实例个数
        'max_instances': 1,
        # 是否运行一次最新的任务，当多个任务堆积时
        'coalesce': True,
        # 默认值的设置很科学啊
    }
)
import asyncio
# export().scheduler = scheduler

async def _start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.opt(colors=True).info("<y>Scheduler Started</y>")
driver = get_driver()
driver.on_startup(_start_scheduler)