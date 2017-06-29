# -*- coding: utf-8 -*-
import random
from functools import partial

import TimerDefine
import guildAdviserDealConfig
import guildConfig
import guildNPCConfig
import math
from KBEDebug import INFO_MSG, WARNING_MSG
import ErrorCode
from KBEDebug import ERROR_MSG
import util
import KBEngine
from interfaces.BaseModule import BaseModule

__author__ = 'chongxin'
__createTime__  = '2017年3月29日'

class PowerEnmu:
    leader          = 5 # 领袖
    secondLeader    = 4 # 副统领
    director        = 3 # 理事
    deacon          = 2 # 执事
    elite           = 1 # 精英
    member          = 0 # 成员

class GuildTaskType:
    Appeal      = 1      # 上诉
    Exposure    = 2      # 曝光
    Donate      = 3      # 捐款
    Ingratiate  = 4      # 讨好
    Interact    = 5      # 互动
    Instigate   = 6      # 挑拨


class BuildEnmu:
    Hall       = 1 # 公会大厅
    Shop       = 2 #公会商城
    Consultant = 3 #顾问大厅
    Task       = 4 #任务大厅
    WorldCup   = 5 #中国梦之世界杯


"""
公会管理器
"""
class GuildMgr(BaseModule):

    def __init__(self):
        KBEngine.Base.__init__(self)
        KBEngine.globalData["GuildMgr"] = self

        self.dbidToMb = {}

        # 根据dbid找到item
        self.dbidToIndex = {}

        self.rebuildDBIDToIndex()


    # 初始化NPC公会
    def iniNPCGuild(self):

        for id ,item in guildNPCConfig.GuildNPCConfig.items():
            guildParam = {
                "level": 1,
                "camp": item["campe"],
                "name": item["name"],
                "configID":id,
                "isGuildNPC":1
            }
            # 创建公会实体
            guild = KBEngine.createBaseLocally("Guild", guildParam)

            def guildWriteToDB_CB(success, guild):
                values={
                    "dbid":guild.databaseID,
                    "configID":guild.configID
                }
                WARNING_MSG("--iniNPCGuild-dbid-configID--:"+str(guild.databaseID)+"---"+str(guild.configID))
                self.guildNPCList.append(values)
                guild.onCreatGuildAdviser(values)
                self.dbidToMb[guild.databaseID] = guild
                self.writeToDB()


            guild.writeToDB(guildWriteToDB_CB,True)



    def initNPCGuildAdviser(self,argMap):

        for item in self.guildNPCList:
            guildDBID = item["dbid"]
            def CB(guild, guildDBID, wasActive):
                if guildDBID not in self.dbidToMb:
                    self.dbidToMb[guildDBID] = guild
                    guild.onCmd("onCreatGuildAdviser", argMap)
            if guildDBID not in self.dbidToMb:
                KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
            else:
                guildMb = self.dbidToMb[guildDBID]
                guildMb.onCmd("onCreatGuildAdviser", argMap)

        self.autoNPCGuildBehavior()

    # NPC公会行为
    def autoNPCGuildBehavior(self):

        hour = util.getNowHour() + 0.1
        ran_num = random.randint(0, 4)
        nextHour = math.ceil(hour/4) * 4 + ran_num
        offset = (nextHour-hour) * 60 * 60 + random.randint(0, 300)
        self.addTimer(offset, 4 * 60 * 60, TimerDefine.Timer_guildNPC_behavior)

        pass

    def onTimer(self, tid, userArg):
        if userArg == TimerDefine.Timer_guildNPC_behavior:

            self.delTimer(tid)
            self.autoNPCGuildBehavior()
            self.npcGuildBehavior()
            self.npcGuildInciteAdviser()

    # NPC公会上诉曝光行为
    def npcGuildBehavior(self):

        for item in self.guildNPCList:
            guildDBID =  item["dbid"]
            guildNPCInfo = guildNPCConfig.GuildNPCConfig[item["configID"]]

            param = {
                "guildDBID" : guildDBID,
                "guildName" :guildNPCInfo["name"]
            }

            self.npcGuildAppealBehavior(param)

        pass

    def npcGuildAppealBehavior(self,argMap):

        WARNING_MSG("--npcGuildAppealBehavior-guildName-"+str(argMap["guildName"]))

        for item in self.guildInfoList:
            guildDBID = item["dbid"]
            if item["level"] < 3 :
                continue

            param = {"attackIsNPC": 1,
                     "appeadID": 1,
                     "playerMB": None,
                     "guildName": argMap["guildName"],
                     "guildDBID" : guildDBID
                     }
            param1 = {"attackIsNPC": 1,
                      "playerMB": None,
                      "appeadID": 3,
                      "guildName": argMap["guildName"],
                      "guildDBID": guildDBID
                      }

            WARNING_MSG("--npcGuildAppealBehavior--guildDBID:"+str(guildDBID)+"--guildName-"+str(argMap["guildName"]))

            self.onCmdGuildAppealExposure(param)
            self.onCmdGuildAppealExposure(param1)

        pass

    # NPC公会挑拨顾问
    def npcGuildInciteAdviser(self):
        dealInfo = guildAdviserDealConfig.GuildAdviserDealConfig[7]
        adviserMgr = KBEngine.globalData["AdviserMgr"]

        for item in self.guildNPCList:
            guildDBID = item["dbid"]
            guildNPCInfo = guildNPCConfig.GuildNPCConfig[item["configID"]]
            param = {
                "guildDBID": guildDBID,
                "playerMB": None,
                "adviserDBID": 0,
                "dealId": 7,
                "subamity": dealInfo["subamity"],
                "amity": dealInfo["addamity"],
                "guildName": guildNPCInfo["name"]
            }

            adviserMgr.npcGuildIncite(param)


        pass





    # 获取公会信息
    def onCmdGetGuildInfo(self,argMap):
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        param = {"playerMB" : playerMB}
        def CB( guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("getGuildInfo",param)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("getGuildInfo",param)

    # 获取公会成员信息
    def onCmdGetGuildMember(self,argMap):
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("getGuildMemberList", playerMB)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("getGuildMemberList", playerMB)


    #     获取公会副会长和介绍信息
    def onCmdGetGuildViceInfo(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("getGuildViceIntroduce", playerMB)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("getGuildViceIntroduce", playerMB)



    # 获取公会申请列表
    def onCmdGuildApplyList(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        guildPower = argMap["guildPower"]

        if guildPower < PowerEnmu.secondLeader:
            return

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("getGuildApplyList", playerMB)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("getGuildApplyList", playerMB)



    # 根据阵营申请公会列表
    def onCmdGuildList(self,argMap):

        camp = argMap["camp"]
        playerMB        = argMap["playerMB"]

        findItem = []
        for item in self.guildInfoList:
            if  item["camp"] == camp:
                findItem.append(item)

        playerMB.client.onFindCamp(len(findItem),findItem)

    # 创建公会
    def onCmdCreateGuild(self,argMap):
        # 验证是否重名
        playerMB        = argMap["playerMB"]
        playerDBID      = argMap["playerDBID"]
        playerLevel     = argMap["playerLevel"]
        officalPosition = argMap["officalPosition"]
        playerName      = argMap["playerName"]
        camp            = argMap["camp"]
        guildName       = argMap["guildName"]
        introduction    = argMap["introduction"]
        # 重名 创建失败
        for item in self.guildInfoList:
            if item["guildName"] == guildName:
                playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_repeat_name)
                return

        guildParam = {
            "level"             : 1,
            "camp"              : camp,
            "name"              : guildName,
            "leader"            : playerName,
            "introduction"     : introduction,
            "ropeTimes"        : guildConfig.GuildConfig[1]["ropeTime"]
        }

        def onCreateBaseCallback(guild):

            if guild == None :
                WARNING_MSG("-guildWriteToDB_CB--onCreateBaseCallback----")
                return

            def guildWriteToDB_CB(success, guild):
                ERROR_MSG("  create success " + str(guild.databaseID))
                value = {"dbid": guild.databaseID,
                         "guildName": guildName,
                         "camp": camp,
                         "level": 1,
                         "count": 1,
                         "leader": playerName,

                         }
                # 保存到数据库（自动）
                self.createGuild(value)
                #
                self.dbidToMb[guild.databaseID] = guild

                #    把自己加入公会中
                argMap = {
                    "selfDBID": playerDBID,
                    "applyerDBID": playerDBID,
                    "result": 1,
                    "playerName": playerName,
                    "offical": officalPosition,
                    "level": playerLevel,
                    "power": PowerEnmu.leader,
                    "playerMB": playerMB
                }
                #  公会信息改变刷新
                guild.onCmd("updateGuildValueRank", {})
                guild.onCmd("onCreatGuildAdviser", {})
                guild.onCmd("onCreateGuildBuild",{})
                guild.onCmd("agreeJoin", argMap)

                guildParam={
                    "guildDBID" : guild.databaseID,
                    "power":  int(PowerEnmu.leader),
                    "guildLevel": int(PowerEnmu.leader),
                    "guildName": guildName
                }
                playerMB.onPlayerMgrCmd("setGuildDBID", guildParam)

                # playerMB.guildDBID = guild.databaseID
                # playerMB.guildPower = int(PowerEnmu.leader)
                # playerMB.guildName = guildName
                # playerMB.guildLevel = 1

                self.writeToDB()

            guild.writeToDB(guildWriteToDB_CB)


        # 创建公会实体
        KBEngine.createBaseAnywhere("Guild",guildParam,onCreateBaseCallback)




    # 申请加入公会
    def onCmdApplyJoinGuild(self,argMap):
        playerMB            = argMap["playerMB"]
        guildDBID           = argMap["guildDBID"]
        playerDBID          = argMap["playerDBID"]
        playerLevel         = argMap["playerLevel"]
        officalPosition     = argMap["officalPosition"]
        playerName          = argMap["playerName"]
        camp                = argMap["camp"]

        if self.isGuildExist(guildDBID) is False:
            ERROR_MSG("----------------not exist guild ---------------------------")
            playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_guild_not_exist)
            return

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, partial(self.applyJoinGuildCB,argMap))

        else:
            guildMb = self.dbidToMb[guildDBID]
            self.applyJoinGuildCB(argMap, guildMb, guildDBID, True)

    # 申请加入公会回调
    def applyJoinGuildCB(self,argMap,guild,guildDBID,wasActive):
        playerMB = argMap["playerMB"]
        applyInfo = {
            "dbid"          : argMap["playerDBID"],
            "playerName"    : argMap["playerName"],
            "offical"       : argMap["officalPosition"],
            "level"         : argMap["playerLevel"],
            "applyTime"     : util.getCurrentTime(),
            "playerMB"      : playerMB,
        }
        guild.onCmd("applyJoinGuild",applyInfo)



    #  刷新公会人数
    def onCmdRefreshGuildCount(self,argMap):

        guildDBID =  argMap["guildDBID"]
        count =  argMap["count"]

        if guildDBID not in self.dbidToIndex:
            return

        guildInfo = self.findGuildByDBID(guildDBID)
        if guildInfo == None :
            return

        guildInfo["count"] = count

    # 刷新公会名字
    def refreshGuildName(self,argMap):
        guildDBID = argMap["guildDBID"]
        gulldName = argMap["guildName"]

        if guildDBID not in self.dbidToIndex :
            return

        guildInfo = self.findGuildByDBID(guildDBID)

        if guildInfo == None:
            return
        guildInfo["guildName"] = gulldName

     # 刷新公会等级
    def refreshGuildLevel(self, argMap):
        guildDBID = argMap["guildDBID"]
        level = argMap["level"]

        if guildDBID not in self.dbidToIndex:
            return

        guildInfo = self.findGuildByDBID(guildDBID)

        if guildInfo == None:
            return
        guildInfo["level"] = level

     # 刷新公会领袖
    def refreshGuildLeader(self, argMap):
        guildDBID = argMap["guildDBID"]
        leader = argMap["leader"]

        if guildDBID not in self.dbidToIndex :
            return

        guildInfo = self.findGuildByDBID(guildDBID)

        if guildInfo == None:
            return
        guildInfo["leader"] = leader

    # 离开公会
    def onCmdLeaveGuild(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        playerDBID = argMap["playerDBID"]

        if self.isGuildExist(guildDBID) is False:
            ERROR_MSG("----------------not exist guild ---------------------------")
            playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_guild_not_exist)
            return

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, partial(self.leaveGuildCB,argMap))
        else:
            guildMb = self.dbidToMb[guildDBID]
            self.leaveGuildCB(argMap, guildMb, guildDBID, True)


    def leaveGuildCB(self, argMap, guild, guildDBID, wasActive):

        if guildDBID not in self.dbidToMb:
            self.dbidToMb[guildDBID] = guild

        del argMap["guildDBID"]
        guild.onCmd("leaveGuild",argMap)



    def onCmdAgreeJoin(self,argMap):
        playerMB    = argMap["playerMB"]
        guildDBID   = argMap["guildDBID"]
        applyerDBID = argMap["applyerDBID"]

        if self.isGuildExist(guildDBID) is False:
            ERROR_MSG("----------------not exist guild ---------------------------")
            playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_guild_not_exist)
            return

        param = {
            "applyerDBID": applyerDBID,
            "power": PowerEnmu.member,
            "selfDBID": argMap["selfDBID"],
            "playerMB": playerMB

        }

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("agreeJoin", param)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("agreeJoin", param)



    # 拒绝申请
    def onCmdRejectApply(self,argMap):
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        applyerDBID = argMap["applyerDBID"]
        if self.isGuildExist(guildDBID) is False:
            ERROR_MSG("----------------not exist guild ---------------------------")
            playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_guild_not_exist)
            return

        param = {
                  "applyerDBID": applyerDBID,
                   "playerMB":playerMB
         }

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
                guild.onCmd("rejectApply", param)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("rejectApply", param)


    # 取消申请
    def onCmdCancelApply(self,argMap):
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        applyerDBID = argMap["applyerDBID"]
        if self.isGuildExist(guildDBID) is False:
            ERROR_MSG("----------------not exist guild ---------------------------")
            playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_guild_not_exist)
            return

        param = {"applyerDBID": applyerDBID}

        def cancelApplyCB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild

            guild.onCmd("cancelApply",param)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, cancelApplyCB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("cancelApply",param)
        pass

    # 查找同阵营公会
    def onCmdFindCamp(self,argMap):
        keyWord = argMap["keyWord"]
        playerMB  = argMap["playerMB"]
        camp = argMap["camp"]

        findItem = []
        for item in self.guildInfoList:
            name = item["name"]

            if name.find(keyWord) and item["camp"] == camp:
                findItem.append(item)

        playerMB.client.onFindCamp(len(findItem),findItem)

    # 清除公会周贡献
    def onCmdClearWeekDonate(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("clearWeekDonate", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guild = self.dbidToMb[guildDBID]
            guild.onCmd("clearWeekDonate", argMap)




    # 清除公会日贡献
    def onCmdClearDayDonate(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("clearDayDonate", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guild = self.dbidToMb[guildDBID]
            guild.onCmd("clearDayDonate", argMap)

    # 刷新公会每日拉拢次数
    def onCmdRefreshRopeTimes(self,argMap):

        guildDBID = argMap["guildDBID"]
        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("refreshRopeTimes", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guild = self.dbidToMb[guildDBID]
            guild.onCmd("refreshRopeTimes", argMap)



    # 修改公会简介和公告
    def onCmdChangeNotice(self,argMap):
        playerMB = argMap["playerMB"]

        guildDBID = argMap["guildDBID"]
        del argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("changeNotice", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("changeNotice", argMap)



    # 修改公会名字
    def onCmdChangeGuildName(self,argMap):
        guildDBID = argMap["guildDBID"]
        guildName = argMap["guildName"]
        playerMB  = argMap["playerMB"]

        del argMap["guildDBID"]
        # 重名检查
        for item in self.guildInfoList:
            if item["guildName"] == guildName:
                playerMB.client.onGuildError(ErrorCode.GuildModuleError.Guild_repeat_name)
                return

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("changeGuildName", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("changeGuildName", argMap)



    def onCmdKickOut(self,argMap):
        playerDBID = argMap["playerDBID"]
        selfDBID   = argMap["selfDBID"]
        playerMB   = argMap["playerMB"]
        guildDBID  = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("kickOut", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("kickOut", argMap)



    # 退出公会
    def onCmdQuitGuild(self,argMap):
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("quitGuild", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("quitGuild", argMap)



    #  公会 任命
    def onCmdAppointPower(self,argMap):
        playerDBID = argMap["playerDBID"]
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID  = argMap["guildDBID"]

        power = argMap["power"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("appoinPower", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("appoinPower", argMap)




    #  公会转让
    def onCmdGuildTransfer(self,argMap):

        playerDBID = argMap["playerDBID"]
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildTransfer", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildTransfer", argMap)



    # 解散公会
    def onCmdDismissGuild(self,argMap):

        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("dismissGuild", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("dismissGuild", argMap)



    # 取消解散公会
    def onCmdCancelDismiss(self, argMap):

        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("cancelDismiss", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("cancelDismiss", argMap)



    #  公会捐钱
    def onCmdGuildDonate(self,argMap):

        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        euro = argMap["euro"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildDonate", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)

        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildDonate", argMap)





    #  公会建筑升级
    def onCmdBuildUpgrade(self,argMap):

        playerDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        buildID = argMap["buildID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildBuildUpgrade", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildBuildUpgrade", argMap)



    # 公会建筑升级加速
    def onCmdBuildSpeed(self,argMap):

        playerDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        buildID = argMap["buildID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildBuildSpeed", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)

        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildBuildSpeed", argMap)




    # 检查公会建筑升级情况
    def onCmdCheckBuild(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildCheckBuildUpgrade", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildCheckBuildUpgrade", argMap)

    # 请求公会保护时间
    def onCmdGuildProtectTime(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildProtectTime", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildProtectTime", argMap)
        pass


    # 检查公会保护时间
    def onCmdCheckProtectTime(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("checkProtectTime", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("checkProtectTime", argMap)




    # 公会解散检查
    def onCmdCheckGuildDismiss(self,argMap):
        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("checkGuildDismiss", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("checkGuildDismiss", argMap)



        pass

    # 成员下线状态
    def onCmdChangeOnlineState(self,argMap):

        guildDBID = argMap["guildDBID"]

        for item in self.guildNPCList:
            if item["configID"] == guildDBID:
                guildDBID =  item["dbid"]

        WARNING_MSG(util.printStackTrace("onCmdChangeOnlineState"))

        def cancelApplyCB(guild, guildDBID, wasActive):

            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild

            guild.onCmd("onChangeOnlineState",argMap)


        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, cancelApplyCB)
        else:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("onChangeOnlineState",argMap)

    # 公会上诉曝光
    def onCmdGuildAppealExposure(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildAppealExposure", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildAppealExposure", argMap)

        pass

    # 公会购买公会保护
    def onCmdGuildBuyProtect(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildBuyProtect", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildBuyProtect", argMap)



    # 弹劾
    def onCmdImpeach(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("impeach", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("impeach", argMap)


        pass

    #公会升级
    def onCmdGuildUpdate(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guiildUpdate", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)

        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guiildUpdate", argMap)

        pass


    # GM增加公会资金
    def onCmdGMAddGuildFunds(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("addGuildFunds", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("addGuildFunds", argMap)


        pass

      # GM增加公会声望
    def onCmdGMAddGuildReputation(self, argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("addGuildReputation", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("addGuildReputation", argMap)


        pass

    # 公会顾问处理
    def onCmdGuildAdvieserDeal(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("upDateGuildAdviser", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("upDateGuildAdviser", argMap)

        pass

    # 顾问拉拢
    def onCmdGuildAdvieserRope(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("adviserRope", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("adviserRope", argMap)
        pass


    # 公会顾问好友度
    def onCmdGuildAdvieser(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildAdviser", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildAdviser", argMap)

    #  设置公会顾问目标
    def onCmdAdvieserTarget(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("advieserTarget", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("advieserTarget", argMap)

        pass

    # 设置顾问友好度
    def onCmdAdvieserFriend(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("advieserFriend", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("advieserFriend", argMap)

        pass
    # 已发布任务列表

    def onCmdTaskIDIssueList(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("taskIdIssueList", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("taskIdIssueList", argMap)

    # 发布公会任务
    def onCmdSetTask(self,argMap):
        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("setTask", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("setTask", argMap)

    #  公会任务
    def onCmdGuildTask(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildTask", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildTask", argMap)

        pass

    # 公会任务完成
    def onCmdGuildTaskFinsh(self,argMap):

        guildDBID = argMap["guildDBID"]

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildTaskFinish", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildTaskFinish", argMap)

        pass

    # 公会顾问事件
    def onCmdAdviserEvent(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildAdviserEvent", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildAdviserEvent", argMap)

        pass

    # 公会政事事件
    def onCmdGuildEvent(self,argMap):

        guildDBID =  self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("saveGuildEvent", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("saveGuildEvent", argMap)

        pass


    #  公会事件侦查
    def onCmdSpyGuildEvent(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("spyGuildEvent", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("spyGuildEvent", argMap)

    # 公会人事事件

    def onCmdGuildHrEvent(self,argMap):
        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildHrEventList", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildHrEventList", argMap)

    #公会顾问事件
    def onCmdGuildAdviserEvent(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildAviserEventList", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildAviserEventList", argMap)

        pass

    # 公会政务事件
    def onCmdGuildGovernEvent(self,argMap):
        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("guildGovernEvent", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("guildGovernEvent", argMap)

        pass

    # NPC公会拉拢顾问
    def onCmdNPCRopeAdviser(self,argMap):
        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("npcRopeAdviser", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("npcRopeAdviser", argMap)
        pass


    # 刷新前顾问归属公会 顾问信息
    def onCmdRefreshGuildAviser(self,argMap):

        guildDBID = self.getGuildDBID(argMap["guildDBID"])

        def CB(guild, guildDBID, wasActive):
            if guildDBID not in self.dbidToMb:
                self.dbidToMb[guildDBID] = guild
            guild.onCmd("refreshGuildAviser", argMap)

        if guildDBID not in self.dbidToMb:
            KBEngine.createBaseAnywhereFromDBID("Guild", guildDBID, CB)
        else:
            guildMB = self.dbidToMb[guildDBID]
            guildMB.onCmd("refreshGuildAviser", argMap)
        pass


    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def isGuildExist(self,guildDBID):
        for item in self.guildInfoList:
            if item["dbid"] == guildDBID:
                return True
        return False

    # 重置查询列表
    def rebuildDBIDToIndex(self):

        for i in range(len(self.guildInfoList)) :
            item = self.guildInfoList[i]
            dbid = item["dbid"]
            self.dbidToIndex[dbid] = i


    # 增加一个公会
    def createGuild(self,itemInfo):
        dbid = itemInfo["dbid"]
        self.guildInfoList.append(itemInfo)
        ERROR_MSG("--CreatGUild self.guildInfoList--"+str(len(self.guildInfoList)))

        self.dbidToIndex[dbid] = len(self.guildInfoList) -1
    # 移除公会
    def dismissGuild(self,guildID):
        if guildID not in self.dbidToIndex:
            return
        index =  self.dbidToIndex.pop(guildID)

        self.guildInfoList.pop(index)

        self.rebuildDBIDToIndex()

    def findGuildByDBID(self,guildID):
        if guildID in self.dbidToIndex:
            index = self.dbidToIndex[guildID]
            if index > len(self.guildInfoList):
                return None
            else:
                return self.guildInfoList[index]
        else:
            return None

    def getGuildDBID(self,guildId):
        for item in self.guildNPCList:
            if item["configID"] == guildId:
                return item["dbid"]

        return guildId


