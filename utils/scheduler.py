from nonebot import get_driver, export
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from nonebot.log import logger
# scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
import asyncio
# export().scheduler = scheduler

async def _start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.opt(colors=True).info("<y>Scheduler Started</y>")
driver = get_driver()
driver.on_startup(_start_scheduler)