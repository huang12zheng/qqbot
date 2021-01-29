from utils.bot_io import readfile
from nonebot.adapters.cqhttp import Bot
class VipHandle:
    Inited = False
    def init(self,bot:Bot,config,service_count={}):
        self.bot=bot
        self.config=config
        self.service_count=service_count
        self.getfile()
        Inited = True
        # self.vip=vip
    async def handle_service_count(self,uid,gid):
        if not uid in self.service_count:
            self.service_count[uid] = 0
        else:
            self.service_count[uid] += 1
        if self.service_count[uid] == self.config.jjcservicemax and not uid in self.vip:
            await self.bot.send_msg(
                message_type="group",
                group_id=gid,
                user_id=uid,
                message="千歌酱太辛苦了,没有时间更优秀\n..报歉..今天没时间陪你了"
            )
    def check_service_count(self,uid):
        if not uid in self.service_count:
            self.service_count[uid] = 0
        if (not uid in self.vip) and self.service_count[uid] == self.config.jjcservicemax:
            return False
        return True
    def getfile(self):
        self.vip = readfile('','vip.json')
    def get_service_count(self):
        return self.service_count