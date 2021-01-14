


#################### Command Set B ####################
noticehelp = on_command('notice帮助',aliases={'订阅帮助',"通知帮助","nh"})
add_sub=on_command('通知订阅',aliases={'noticebind','nb '})
delete_sub=on_command('停止通知订阅',aliases={'unnoticebind','unb '})
sub_status=on_command('订阅状态')
notice_config_reload=on_command('通知配置重载',aliases={"notice_reload","nr "})
#################### Command Set E ####################
#################### Init Begin ####################
Inited = False
notices = {}
arena_ranks_bynotice = {}
grand_arena_ranks_bynotice ={}
isCanNoticeBind:bool = True

sv_help = '''
[通知订阅 人名 uid] 绑定竞技场排名变动推送（仅下降），默认双场均启用
[停止通知订阅 人名] 停止战斗竞技场排名变动推送
[订阅状态] 查看排名变动推送绑定状态
'''.strip()

def Init():
    global Inited
    global notices
    global tr
    Inited = True
    config_path = path.join(path.dirname(__file__),"notices.json")
    with open(config_path,"r",encoding="utf8")as fp:
        notices = json.load(fp)

@noticehelp.handle()
async def send_help(bot: Bot, event: Event, state: dict):
    await bot.send(event, sv_help)

# @notice_config_reload.handle() # 因为是volumn的, 所以要重新部署
#################### Init End ####################
#################### Notice Set B ####################

@switch_bind.handle()
async def on_switch_bind(bot: Bot, event: Event, state: dict):
    global isCanNoticeBind
    isCanNoticeBind = not isCanNoticeBind
    await bot.send(event,f"noticeState is {isCanNoticeBind}")

def save_notices():
    config_path = path.join(path.dirname(__file__),"notices.json")
    jsonStr = json.dumps(notices, indent=4)
    with open(config_path,"r+",encoding="utf8")as fp:
        fp.truncate(0)
        fp.seek(0)
        fp.write(jsonStr)():

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
        if not id in notices[gid]:
            notices[uid] = { "username": username, "arena_on": True, "grand_arena_on": True }
        else:
            notices[id]["username"] = id
            notices[id]["arena_on"] = uid
            notices[id]["grand_arena_on"]
    save_notices()
    await bot.send(event,"通知绑定成功",at_sender=True)

@delete_sub.handle()
async def on_delete_sub(bot: Bot, event: Event, state: dict):
    if not Inited:
        Init()
    gid = str(event.group_id)
    if not gid in notices:
        await bot.finish(event, "您还未设置通知订阅", at_sender=True)
        return
    else:
    if len(event.message) == 1 and event.message[0].type == 'text' and not event.message[0].data['text']:
        uid = str(event.message)
        if not id in notices:
            await bot.finish(event, "您还未设置通知订阅", at_sender=True)
            return
        else:
            notices[group].pop(uid)
            save_notices()
            await bot.send(event, "删除竞技场订阅成功", at_sender=True)
    else:
        await bot.finish(event, '参数格式错误, 请重试')

#################### Notice Set E ####################
#################### Sub B ####################
def on_arena_schedule():
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
    tasks=[]
    async def tasks_prepare(notices):
        for group in notices:
            group = str(group)
            gid   = int(group)
            for user in notices[group]:
                user = str(user)
                if notices[group][user]["arena_on"] or notices[group][user]["grand_arena_on"]:
                    await asyncio.create_task(check_arena_state(bot,group,user))
                    await asyncio.sleep(1)
                else:
                    # { group:{user: rank} }
                    if group in arena_ranks_bynotice:
                        if user in arena_ranks_bynotice[group]: del arena_ranks_bynotice[group][user]
                    if group in grand_arena_ranks_bynotice:
                        if user in grand_arena_ranks_bynotice[group]: del grand_arena_ranks_bynotice[group][user]
                    
    asyncio.run(tasks_prepare())   ### main entrance
    logger.opt(colors=True).info("<r>-----------------------------------------------------</r>")
    
async def check_arena_state(bot,group,user):
    try:
        gid = int(group)
        uid = int(user)
        res = await getprofile(uid)
        if type(res) is str and  res.startswith('queue'):
            logger.info(f"{res}成功添加至队列")
            return
        res = res["user_info"]
        # arena_ranks_bynotice is data_set
        ## arena_ranks_bynotice key is what? 
        ## GA notice  ## GB is need to notice too

        def template_handle(template:str):
            def msg_handle(username,origin_rank,new_rank):
                return template.format(username=username,origin_rank=origin_rank,new_rank=new_rank)
            return msg_handle
                # f"{username}的竞技场排名发生变化：{origin_rank}->{new_rank}"
        notice_task(
            bot,
            on_flag=notices[group][user]["arena_on"],
            data_set=arena_ranks_bynotice[group],
            key = notices[group][user]['usernmae'],
            value = res["user_info"]["arena_rank"],
            msg_handle=template_handle("{usernmae}的技场排名发生变化：{origin_rank}->{new_rank}")
        )

        notice_task(
            bot,
            on_flag=notices[group][user]["arena_on"],
            data_set=grand_arena_ranks_bynotice[group],
            key = notices[group][user]['usernmae'],
            value = res["user_info"]["grand_arena_rank"],
            msg_handle=template_handle("{usernmae}的公主竞技场排名发生变化：{origin_rank}->{new_rank}")
        )
    except Exception as inst:
        logger.info("对{group}.{user}的检查出错")
        print(inst)


#################### Sub E ####################
# on_flag
# data_set
# msg_handle
## bot.send_msg
async def notice_task(bot,on_flag,data_set,key,value,msg_handle):
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
                msg = msg_handle(username=key,origin_rank,new_rank)
                data_set[key] = new_rank
                await bot.send_msg(
                    message_type="group",
                    group_id=gid,
                    message=msg
                )

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
driver = nonebot.get_driver()

def _start_scheduler():
    if not Inited:
        Init()
    if not scheduler.running:
        scheduler.add_job(on_arena_schedule,'interval',seconds=driver.config.jjcinterval)
        
        scheduler.start()
        logger.opt(colors=True).info("<y>Notice Scheduler Started</y>")

driver.on_startup(_start_scheduler)