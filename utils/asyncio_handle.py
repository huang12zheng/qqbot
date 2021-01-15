# # from src.plugins.arena_sub import start_scheduler as asyncio1
# # from src.plugins.notice import start_scheduler as asyncio2
from utils.scheduler import scheduler
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
# # import nonebot
import asyncio
import time

tasks=[]
# # def asyncio_handle():
# @scheduler.scheduled_job('interval',seconds=10)
# def schedule_asyncio():
#     if scheduler.state == 2:
#         print('run into a error')
#     async def main():
#         global tasks
#         _tasks=tasks
#         for task in _tasks:
#             print(task.cr_code.co_filename)
#             await task
#         await asyncio.gather()
#             tasks.remove(task)
#         # await asyncio.sleep(1)
#         print('before resume run')
#         print(f'23 {scheduler.state}')
#         print(f'len(tasks):{len(tasks)}')
#         scheduler.resume()
#         print(f'25 {scheduler.state}')
#     # print(time.time())
#     if len(tasks)>0:
#         print(f'---------------------------------start-----------------------------------')
#         print(f'{len(tasks)}')
#         print(f'30 {scheduler.state}')
#         scheduler.pause()
#         print(f'32 {scheduler.state}')
#         print('pause run')
#         asyncio.run(main())
#         print(f'35 {scheduler.state}')
#         print(f'--------------------------------- end -----------------------------------')

isCanLog:bool = False
switch_log=on_command('sl_scheduled')

@switch_log.handle()
async def switch_log(bot: Bot, event: Event, state: dict):
    global isCanLog
    isCanLog = not isCanLog
    await bot.send(event,f"isCanLog is {isCanLog}")

@scheduler.scheduled_job('interval',seconds=10)
def schedule_asyncio():
    # isLog=False
    if scheduler.state == 2:
        print('run into a error')
    global isCanLog
    async def main():
        global tasks
        async def run_taskWithRemove(task):
            if isCanLog:print(task.cr_code.co_filename)
            await task
            tasks.remove(task)
        async def run_gather():
            _tasks=tasks
            for task in _tasks:
                await run_taskWithRemove(task)
                # atasks.append(
                # can't use
                # asyncio.create_task(run_taskWithRemove(task))
                # ))
                # if isCanLog:print(task.cr_code.co_filename)
                # await task
                # tasks.remove(task)
            # asyncio.create_task()
        ## gather() argument after * must be an iterable, not NoneType
        # task = await run_wait()
        # await asyncio.gather(*task)
        # await asyncio.gather(run_wait())
        await run_gather()

        # tasks=[] remove in run_wait
            # tasks.remove(task)
        # await asyncio.sleep(1)
        # print('before resume run')
        # print(f'23 {scheduler.state}')
        # print(f'len(tasks):{len(tasks)}')
        if isCanLog:print(f'--------------------------------- end -----------------------------------')
        scheduler.resume()
        # then ,get a => Execution of job "schedule_asyncio (trigger: interval[0:00:10], next run at: 2021-01-15 09:58:47 CST)" skipped: maximum number of running instances reached (1)
        # print(f'25 {scheduler.state}')
    # print(time.time())
    if len(tasks)>0:
        if isCanLog:print(f'---------------------------------start-----------------------------------')
        print(f'{len(tasks)}')
        # print(f'30 {scheduler.state}')
        scheduler.pause()
        # print(f'32 {scheduler.state}')
        # print('pause run')
        asyncio.run(main())
        # print(f'35 {scheduler.state}')
