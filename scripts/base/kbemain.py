# -*- coding: utf-8 -*-
import KBEngine
import Watcher
import gc
from KBEDebug import *

isGuildMgrLoad = False
isRankMgrLoad = False
isArenaMgrLoad = False
isAdviserMgrLoad = False
isWorldBossMgrLoad = False
isOfficialMgrLoad = False
isLeagueMgrLoad = False

def onBaseAppReady(isBootstrap):
    """
    KBEngine method.
    baseapp已经准备好了
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
    INFO_MSG('onBaseAppReady: isBootstrap=%s' % isBootstrap)

    # 安装监视器
    Watcher.setup()

    if isBootstrap:
        # 创建spacemanager
        # KBEngine.createBaseLocally( "Spaces", {} )
        # 创建邮箱系统
        KBEngine.createBaseLocally("PlayerMgr", {})
        # 创建邮箱系统
        KBEngine.createBaseLocally("Mails", {})

        KBEngine.globalData["Onlines"] = set()

        KBEngine.createBaseLocally("GlobalTimerMgr", {})

        KBEngine.createBaseLocally("RoomMgr", {})
        KBEngine.createBaseLocally("AutoRoomMgr", {})


        if isWorldBossMgrLoad is False:
            worldBossMgr = KBEngine.createBaseLocally("WorldBossMgr", {})
            worldBossMgr.writeToDB(None, True)

        if isGuildMgrLoad is False:
            guildMgr = KBEngine.createBaseLocally("GuildMgr", {})
            guildMgr.iniNPCGuild()
            guildMgr.writeToDB(None,True)

        if isRankMgrLoad is False:
            rankMgr = KBEngine.createBaseLocally("RankMgr", {})
            rankMgr.writeToDB(None,True)

        if isArenaMgrLoad is False:
            arenaMgr = KBEngine.createBaseLocally("ArenaMgr", {})
            arenaMgr.loadFakeData()
            arenaMgr.writeToDB(None, True)

        if isAdviserMgrLoad is False:
            adviserMgr = KBEngine.createBaseLocally("AdviserMgr", {})
            adviserMgr.writeToDB(None, True)
            adviserMgr.initAdviserData()

        if isOfficialMgrLoad is False:
            officialMgr = KBEngine.createBaseLocally("OfficialMgr", {})
            officialMgr.writeToDB(None, True)

        if isLeagueMgrLoad is False:
            leagueMgr = KBEngine.createBaseLocally("LeagueMgr", {})
            leagueMgr.writeToDB(None, True)


def onBaseAppShutDown(state):
    """
    KBEngine method.
    这个baseapp被关闭前的回调函数
    @param state:  0 : 在断开所有客户端之前
                         1 : 在将所有entity写入数据库之前
                         2 : 所有entity被写入数据库之后
    @type state: int
    """
    INFO_MSG('onBaseAppShutDown: state=%i' % state)


    # for entityID, entity in KBEngine.entities.items():
    #     print("entityID:%i, entity=%s", entityID, entity)

    ERROR_MSG("======== KBEngine.entities.garbages.items() =======" + KBEngine.entities.garbages.items().__str__())
    KBEngine.entities.garbages.items()



    gc.collect()
    for x in gc.garbage:
        s = str(x)
        # if len(s) > 80: s = s[:77]+'...'
        ERROR_MSG(type(s).__name__ + "  " + s)



def onReadyForLogin(isBootstrap):
    """
    KBEngine method.
    如果返回值大于等于1.0则初始化全部完成, 否则返回准备的进度值0.0~1.0。
    在此可以确保脚本层全部初始化完成之后才开放登录。
    @param isBootstrap: 是否为第一个启动的baseapp
    @type isBootstrap: BOOL
    """
    # if not isBootstrap:
    # 	INFO_MSG('initProgress: completed!')
    # 	return 1.0
    #
    # spacesEntity = KBEngine.globalData["Spaces"]
    #
    # tmpDatas = list(d_spaces.datas.keys())
    # count = 0
    # total = len(tmpDatas)
    #
    # for utype in tmpDatas:
    # 	spaceAlloc = spacesEntity.getSpaceAllocs()[utype]
    # 	if spaceAlloc.__class__.__name__ != "SpaceAllocDuplicate":
    # 		if len(spaceAlloc.getSpaces()) > 0:
    # 			count += 1
    # 	else:
    # 		count += 1
    #
    # if count < total:
    # 	v = float(count) / total
    # 	# INFO_MSG('initProgress: %f' % v)
    # 	return v;
    #
    # INFO_MSG('initProgress: completed!')
    return 1.0

def onAutoLoadEntityCreate(entityType, dbid):
    """
    KBEngine method.
    自动加载的entity创建方法，引擎允许脚本层重新实现实体的创建，如果脚本不实现这个方法
    引擎底层使用createBaseAnywhereFromDBID来创建实体
    """
    ERROR_MSG('onAutoLoadEntityCreate: entityType=%s, dbid=%i' % (entityType, dbid))
    KBEngine.createBaseAnywhereFromDBID(entityType, dbid)

    if entityType == "GuildMgr":
        ERROR_MSG("   GuildMgr is Load  ")
        global  isGuildMgrLoad
        isGuildMgrLoad = True

    if entityType == "RankMgr":
        ERROR_MSG("   RankMgr is Load  ")
        global  isRankMgrLoad
        isRankMgrLoad = True

    if entityType == "ArenaMgr":
        ERROR_MSG("   ArenaMgr is Load  ")
        global  isArenaMgrLoad
        isArenaMgrLoad = True

    if entityType == "AdviserMgr":
        ERROR_MSG("   AdviseMgr is Load  ")
        global  isAdviserMgrLoad
        isAdviserMgrLoad = True

    if entityType == "WorldBossMgr":
        ERROR_MSG("   WorldBossMgr is Load  ")
        global isWorldBossMgrLoad
        isWorldBossMgrLoad = True

    if entityType == "OfficialMgr":
        ERROR_MSG("   OfficialMgr is Load  ")
        global isOfficialMgrLoad
        isOfficialMgrLoad = True

    if entityType == "LeagueMgr":
        ERROR_MSG("   LeagueMgr is Load  ")
        global isLeagueMgrLoad
        isLeagueMgrLoad = True



def onInit(isReload):
    """
    KBEngine method.
    当引擎启动后初始化完所有的脚本后这个接口被调用
    @param isReload: 是否是被重写加载脚本后触发的
    @type isReload: bool
    """
    INFO_MSG('onInit::isReload:%s' % isReload)

def onFini():
    """
    KBEngine method.
    引擎正式关闭
    """
    INFO_MSG('onFini()')

def onCellAppDeath(addr):
    """
    KBEngine method.
    某个cellapp死亡
    """
    WARNING_MSG('onCellAppDeath: %s' % (str(addr)))

def onGlobalData(key, value):
    """
    KBEngine method.
    globalData有改变
    """
    DEBUG_MSG('onGlobalData: %s' % key)

def onGlobalDataDel(key):
    """
    KBEngine method.
    globalData有删除
    """
    DEBUG_MSG('onDelGlobalData: %s' % key)

def onBaseAppData(key, value):
    """
    KBEngine method.
    baseAppData有改变
    """
    DEBUG_MSG('onBaseAppData: %s' % key)

def onBaseAppDataDel(key):
    """
    KBEngine method.
    baseAppData有删除
    """
    DEBUG_MSG('onBaseAppDataDel: %s' % key)

def onLoseChargeCB(ordersID, dbid, success, datas):
    """
    KBEngine method.
    有一个不明订单被处理， 可能是超时导致记录被billing
    清除， 而又收到第三方充值的处理回调
    """
    DEBUG_MSG('onLoseChargeCB: ordersID=%s, dbid=%i, success=%i, datas=%s' % \
                            (ordersID, dbid, success, datas))


