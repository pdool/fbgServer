# -*- coding: utf-8 -*-
from functools import partial
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

        if guildDBID not in self.dbidToMb:
            return

        guildMb = self.dbidToMb[guildDBID]

        guildMb.onCmd("getGuildMemberList", playerMB)

    #     获取公会副会长和介绍信息
    def onCmdGetGuildViceInfo(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]

        if guildDBID not in self.dbidToMb:
            return

        guildMb = self.dbidToMb[guildDBID]

        guildMb.onCmd("getGuildViceIntroduce", playerMB)


    # 获取公会申请列表
    def onCmdGuildApplyList(self,argMap):

        playerMB = argMap["playerMB"]
        guildDBID = argMap["guildDBID"]
        guildPower = argMap["guildPower"]

        if guildPower < PowerEnmu.secondLeader:
            return

        if guildDBID not in self.dbidToMb:
            return

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

        ERROR_MSG("--onCmdGuildList--"+str(len(findItem)))

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
                     "leader"        : playerName
                     }
            # 保存到数据库（自动）
            self.createGuild(value)
            #
            self.dbidToMb[guild.databaseID] = guild
            guild.updateGuildValueRank()
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

            param = {"playerMB": playerMB}
            guild.onCmd("agreeJoin",argMap)
            guild.onCmd("onCreateGuildBuild",param)
            guild.onCmd("getGuildInfo", param)


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
            guildMb.applyJoinGuildCB(argMap, guildMb, guildDBID, True)
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
        if guildDBID not in self.dbidToMb:
            return

        if guildDBID not in self.dbidToIndex:
            return

        guildInfo = self.findGuildByDBID(guildDBID)

        if guildInfo == None :
            return

        guildInfo["count"] = count

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

        if guildDBID in self.dbidToIndex:
            guildMb = self.dbidToMb[guildDBID]
            param = {
                "applyerDBID": applyerDBID,
                "power": PowerEnmu.member,
                "selfDBID": argMap["selfDBID"]
            }
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

        param = {"applyerDBID": applyerDBID}

        if guildDBID in self.dbidToIndex:
            guildMb = self.dbidToMb[guildDBID]
            guildMb.onCmd("rejectApply",param)

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


    def onCmdSetGuildNum(self,argMap):
        guildDBID = argMap["guildDBID"]
        curNum = argMap["num"]

        # for
        # self.guild

    def onCmdChangeNotice(self,argMap):
        playerMB = argMap["playerMB"]

        guildDBID = argMap["guildDBID"]

        if guildDBID not in self.dbidToMb:
            return
        guildMB = self.dbidToMb[guildDBID]

        del argMap["guildDBID"]
        guildMB.onCmd("changeNotice",argMap)

    def onCmdChangeGuildName(self,argMap):
        guildDBID = argMap["guildDBID"]
        if guildDBID not in self.dbidToMb:
            return
        guildMB = self.dbidToMb[guildDBID]

        del argMap["guildDBID"]
        guildMB.onCmd("changeGuildName",argMap)

    def onCmdKickOut(self,argMap):
        playerDBID = argMap["playerDBID"]
        selfDBID   = argMap["selfDBID"]
        playerMB   = argMap["playerMB"]
        guildDBID  = argMap["guildDBID"]
        if guildDBID not in self.dbidToMb:
            return
        guildMB = self.dbidToMb[guildDBID]

        guildMB.onCmd("kickOut", argMap)

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


    def onCmdImpeach(self,argMap):
        guildDBID = argMap["guildDBID"]
        if guildDBID not in self.dbidToMb:
            return
        guildMB = self.dbidToMb[guildDBID]

        guildMB.onCmd("impeach", argMap)
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