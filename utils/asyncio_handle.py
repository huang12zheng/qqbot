# # from src.plugins.arena_sub import start_scheduler as asyncio1
# # from src.plugins.notice import start_scheduler as asyncio2
from utils.scheduler import scheduler
# # import nonebot
import asyncio


tasks=[]
# # def asyncio_handle():
@scheduler.scheduled_job('interval',seconds=3)
def schedule_asyncio():
    async def main():
        global tasks
        _tasks=tasks
        tasks=[]
        [ await task for task in _tasks ]
    if len(tasks)>0:
        print(f'\n\n{len(tasks)}\n\n')
        asyncio.run(main())
