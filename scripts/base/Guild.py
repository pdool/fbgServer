# -*- coding: utf-8 -*-
import KBEngine
import guildConfig
import util
from ErrorCode import GuildModuleError
from GuildMgr import  PowerEnmu
from KBEDebug import ERROR_MSG
from guildBuildConfig import GuildBuildConfig
from interfaces.BaseModule import BaseModule
from part.guild import GuildNotice

__author__ = 'chongxin'
__createTime__  = '2017年3月31日'
"""
单个公会
"""

class Guild(BaseModule):
    def __init__(self):
        self.dbidToIndex = {}
        self.buildIndex()

    # 获取公会信息
    def getGuildInfo(self,applyInfo):
        playerMB = applyInfo["playerMB"]
        playerMB.client.onGetGuildInfo(
            self.level,
            self.name,
            len(self.guildMember),
            self.guildFunds,
            self.reputation,
            self.notice,
        )

    # 获取公会申请人列表
    def getGuildApplyList(self,playerMB):
        playerMB.client.onGuildApplyList(self.applyMember)

    # 获取公会成员列表
    def getGuildMemberList(self,playerMB):
        playerMB.client.onGuildMemberList(self.guildMember)

    # 获取公会副队长和简介
    def getGuildViceIntroduce(self,playerMB):
        playerMB.client.onGuildViceIntroduce(self.vicePresident,self.introduction)
        pass

    # 申请加入公会
    def applyJoinGuild(self,applyInfo):
        playerMB = applyInfo["playerMB"]
        del applyInfo["playerMB"]
        playerDBID = applyInfo["dbid"]

        for item in self.guildMember:
            if item["dbid"] == playerDBID:
                # 通知已经申请过了
                playerMB.client.onResponse(GuildNotice.GuildNotice.you_already_is_member)
                ERROR_MSG("----------------you has in guild ---------------------------")
                return

        for item in self.applyMember:
            if item["dbid"] == playerDBID:
                # 通知已经申请过了
                playerMB.client.onResponse(GuildNotice.GuildNotice.you_has_apply_join)
                ERROR_MSG("----------------you has apply ---------------------------")
                return

        # 【申请成功！等待公会管理回应】；
        self.applyMember.append(applyInfo)

        playerMB.client.onResponse(GuildNotice.GuildNotice.apply_success_wait_for_resp)

    # 离开公会
    def leaveGuild(self,argMap):
        playerMB = argMap["playerMB"]
        playerDBID = argMap["playerDBID"]

        for item in self.guildMember:
            if item["dbid"] == playerDBID:
                # 通知客户端退出成功
                self.leaveGuildMember.append(item)
                playerMB.client.onResponse(GuildNotice.GuildNotice.leave_guild_success)
                # 去除公会的副会长
                if item["power"] == PowerEnmu.secondLeader:
                    secondLeaderName = item["name"]
                    self.vicePresident.remove(secondLeaderName)

                self.buildIndex()
                return


    # 同意加入
    def agreeJoin(self,argMap):
        applyerDBID = argMap["applyerDBID"]
        power = argMap["power"]
        # 判断自己的权利
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]

        if selfDBID in self.dbidToIndex:
            index = self.dbidToIndex[selfDBID]
            member = self.guildMember[index]
            admit = guildConfig.GuildConfig[member["power"]]["admit"]
            if admit != 1:
                # 权限不够
                playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
                return

        # 人数检查
        maxMemberCount = guildConfig.GuildConfig[1]["maxMemberNum"]
        curCount = len(self.guildMember)

        if curCount >= maxMemberCount:

            playerMB.client.onGuildError(GuildModuleError.Guild_is_full)
            return


        def agreeJoinCB(avatar, dbid, wasActive):
            if avatar != None:
                param = {
                    "playerName": avatar.name,
                    "dbid": avatar.databaseID,
                    "offical": avatar.officalPosition,
                    "level": avatar.level,
                    "power": power,
                }
                # 已经在线了(异步调用)
                if wasActive:
                    argMap = {
                        "guildMB"   : self,
                        "guildDBID" : self.databaseID,
                        "power": power,
                    }
                    param["onlineState"] = 1
                    avatar.onPlayerMgrCmd("setGuildDBID",argMap)
                else:
                    avatar.guildDBID = self.databaseID
                    param["onlineState"] = avatar.logoutTime
                    avatar.destroy()

                self.onJoinGuildCB(param)

            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")
        KBEngine.createBaseFromDBID("Avatar",applyerDBID,agreeJoinCB)


    def onJoinGuildCB(self,argMap):
        # 加入成功
        applyerDBID = argMap["dbid"]

        # 移除申请信息
        for item in self.applyMember:
            if applyerDBID == applyerDBID:
                self.applyMember.remove(item)
                break

        # 判断是否曾经加入过
        for item in self.leaveGuildMember:
            if item["dbid"] == applyerDBID:
                item["power"] = argMap["power"]
                item["offical"] = argMap["offical"]
                item["level"] = argMap["level"]
                item["weekDonate"] = 0
                item["onlineState"] = argMap["onlineState"]


                return
        # 没有加入过。直接插入
        memberInfo = {
            "dbid"          : argMap["dbid"],
            "playerName"    : argMap["playerName"],
            "power"         : argMap["power"],
            "offical"       : argMap["offical"],
            "level"         : argMap["level"],
            "weekDonate"    : 0,
            "sumDonate"     : 0,
            "onlineState"  : argMap["onlineState"]
        }
        self.guildMember.append(memberInfo)
        self.buildIndex()

        argMap = {
            "guildDBID": self.databaseID,
            "count": len(self.guildMember)
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdRefreshGuildCount",argMap)

        def onLookUpCB(applyerAvatar):
            # 在线
            if type(applyerAvatar) is not bool:
                applyerAvatar.client.onResponse(GuildNotice.GuildNotice.create_guild_success)

        KBEngine.lookUpBaseByDBID("Avatar",applyerDBID,onLookUpCB)



    def rejectApply(self,argMap):

        applyerDBID = argMap["applyerDBID"]
        playerMB = argMap["playerMB"]
        for item in self.applyMember:
            if item["dbid"] == applyerDBID:
                self.applyMember.remove(item)

                # playerMB.client
                return

    # 创建公会建筑
    def onCreateGuildBuild(self,argMap):
        playerMB = argMap["playerMB"]

        for id,build in GuildBuildConfig.items():
            buildParam = {}
            buildParam["id"] = build["id"]
            buildParam["level"] = build["level"]
            buildParam["endTimes"] = 0
            self.guildBuild.append(buildParam)

            playerMB.client.onClientGuildBuildInfo(buildParam)


#     取消申请
    def cancelApply(self,argMap):
        applyerDBID = argMap["applyerDBID"]

        for item in self.applyMember:
            if item["dbid"] == applyerDBID:
                self.applyMember.remove(item)
                return
    #   修改公告和简介
    def changeNotice(self,argMap):
        playerMB = argMap["playerMB"]

        if "introduction" in argMap:
            self.introduction = argMap["introduction"]
        if "notice"in argMap:
            self.notice = argMap["introduction"]

        playerMB.client.onResponse(GuildNotice.GuildNotice.change_notice_success)

    def changeGuildName(self,argMap):
        guildName = argMap["guildName"]
        self.name =guildName


    def kickOut(self,argMap):
        playerDBID = argMap["playerDBID"]
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        # 检查权限
        if playerDBID not in self.dbidToIndex or selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        kickItem = self.guildMember[self.dbidToIndex[playerDBID]]

        selfPower = myItem["power"]
        kickPower = kickItem["power"]
        selfCanKick = guildConfig.PowerConfig[selfPower]["kick"]
        canKick = guildConfig.PowerConfig[kickPower]["kick"]
        if selfCanKick != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return
        # 如果被踢者也能踢人
        if canKick == 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        self.leaveGuildMember.append(kickItem)
        self.guildMember.remove(kickItem)
        self.buildIndex()

    def onChangeOnlineState(self,argMap):
        playerDBID = argMap[ "playerDBID"]
        onlineState = argMap["onlineState"]
        if playerDBID not in self.dbidToIndex:
            return
        index = self.dbidToIndex[playerDBID]

        item = self.guildMember[index]

        item["onlineState"] = onlineState

    # 弹劾
    def impeach(self,argMap):
        selfDBID = argMap["selfDBID"]
        # 检查自己的权限
        if selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        selfPower = myItem["power"]
        selfCanImpeach= guildConfig.PowerConfig[selfPower]["impeach"]

        playerMB = argMap["playerMB"]
        if selfCanImpeach != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return
        # 检查会长的登录时间
        leaderItem = None
        for item in self.guildMember:
            if item["power"] == PowerEnmu.leader:
                leaderItem = item
                logoutTime = item["onlineState"]
                period = util.getCurrentTime() - logoutTime
                offlineConfig =  guildConfig.PowerConfig[1]["impeachTime"] * 24 * 60 * 60
                if period < offlineConfig:
                    playerMB.client.onGuildError(GuildModuleError.Guild_leader_offline_not_enough)
                    return

        # 取消原领袖
        leaderItem["power"] = PowerEnmu.member
        myItem["power"] = PowerEnmu.leader

        playerMB.client.onResponse(GuildNotice.GuildNotice.impeach_success)

    def updateGuildValueRank(self):
        param = {
            "dbid": self.databaseID,
            "name": self.name,
            "camp": self.camp,
            "level": self.level,
            "leader": self.leader,
            "reputation": self.reputation,
        }
        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateGuildValueRank", param)

    # 重建索引
    def buildIndex(self):
        self.dbidToIndex = {}
        for index in range(len(self.guildMember)):
            dbid = self.guildMember[index]["dbid"]
            self.dbidToIndex[dbid] = index


