# -*- coding: utf-8 -*-
from functools import partial

import guildConfig
from KBEDebug import INFO_MSG
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
                self.client.onGuildError(ErrorCode.GuildModuleError.Guild_repeat_name)
                return

        guildParam = {
            "level"             : 1,
            "camp"              : camp,
            "name"              : guildName,
            "leader"            : playerName,
            "introduction"     : introduction,
        }
        # 创建公会实体
        guild = KBEngine.createBaseLocally("Guild",guildParam)

        def guildWriteToDB_CB(success, guild):

            ERROR_MSG("  create success " + str(guild.databaseID))
            value = {"dbid"         :guild.databaseID,
                     "guildName"    :guildName,
                     "camp"          : camp,
                     "level"         : 1,
                     "count"         : 1,
                     "leader"        : playerName,
                     }
            # 保存到数据库（自动）
            self.createGuild(value)
            #
            self.dbidToMb[guild.databaseID] = guild

            #    把自己加入公会中
            argMap={
                "selfDBID"      : playerDBID,
                "applyerDBID"   : playerDBID,
                "result"         : 1,
                "playerName"     : playerName,
                "offical"        : officalPosition,
                "level"           : playerLevel,
                "power"           : PowerEnmu.leader,
                "playerMB": playerMB
            }
            #  公会信息改变刷新
            guild.updateGuildValueRank()
            playerMB.guildDBID = guild.databaseID
            playerMB.guildPower = int(PowerEnmu.leader)
            guild.onCmd("agreeJoin",argMap)



        guild.writeToDB(guildWriteToDB_CB)


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




    def onCmdSetGuildNum(self,argMap):
        guildDBID = argMap["guildDBID"]
        curNum = argMap["num"]

        # for
        # self.guild
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
        del argMap["guildDBID"]

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


    def onCmd(self, methodName, argMap):
        if hasattr(self, methodName) is False:
            ERROR_MSG("GuildMgr  not exist method  " + methodName)

        func = getattr(self, methodName)

        func(argMap)