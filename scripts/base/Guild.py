# -*- coding: utf-8 -*-
import random

import KBEngine
import guildAppealConfig
import guildConfig
import guildUpCouConfig
import guildUpHallConfig
import guildUpShopConfig
import guildUpTaskConfig
import util
from ErrorCode import GuildModuleError
from GuildMgr import  PowerEnmu, BuildEnmu
from KBEDebug import ERROR_MSG, WARNING_MSG
from guildBuildConfig import GuildBuildConfig
from guildUpgradeConfig import GuildUpgradeConfig
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

        self.buildBDToIndex = {}
        self.creatBuildBDIndex()

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
            self.dismissTime,
            self.databaseID,
            self.introduction,
            self.protectTime,
            self.guildBuild
        )

    # 获取公会申请人列表
    def getGuildApplyList(self,playerMB):
        WARNING_MSG("---getGuildApplyList---"+str(len(self.applyMember)))
        playerMB.client.onGuildApplyList(self.applyMember)

    # 获取公会成员列表
    def getGuildMemberList(self,playerMB):
        playerMB.client.onGuildMemberList(self.guildMember)

    # 获取公会副队长和简介
    def getGuildViceIntroduce(self,playerMB):
        menmBerItems = []
        for item in self.guildMember:
            if item["power"] >= PowerEnmu.secondLeader:
                menmBerItems.append(item)

        playerMB.client.onGuildViceIntroduce(menmBerItems,self.introduction)
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

        ERROR_MSG("--applyJoinGuild-self.applyMemberLen-"+str(len(self.applyMember)))

        playerMB.client.onResponse(GuildNotice.GuildNotice.apply_success_wait_for_resp)

    # 离开公会
    def leaveGuild(self,argMap):
        playerMB = argMap["playerMB"]
        playerDBID = argMap["playerDBID"]

        for item in self.guildMember:
            if item["dbid"] == playerDBID:
                # 通知客户端退出成功
                self.leaveGuildMember.append(item)
                playerMB.guildDBID = 0
                playerMB.guildDonate = 0
                playerMB.guildPower = 0

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

        if power != PowerEnmu.leader:
            isExit = self.isExitApplyInfo(applyerDBID)
            ERROR_MSG("--agreeJoin-isExit-"+str(isExit))
            if isExit == 0:
                playerMB.client.onGuildError(GuildModuleError.Guild_applye_by_cancel)
                return

        if applyerDBID in  self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_already_in_guild)
            return

        if selfDBID in self.dbidToIndex:
            index = self.dbidToIndex[selfDBID]
            member = self.guildMember[index]
            admit = guildConfig.PowerConfig[member["power"]]["admit"]
            if admit != 1:
                # 权限不够
                playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
                return

        # 人数检查
        maxMemberCount = self.guildMaxMember()
        curCount = len(self.guildMember)

        if curCount >= maxMemberCount:
            playerMB.client.onGuildError(GuildModuleError.Guild_is_full)
            return


        def agreeJoinCB(avatar, dbid, wasActive):
            if avatar != None:
                WARNING_MSG("--agreeJoinCB--"+str(avatar.guildDBID))

                param = {
                    "playerName": avatar.name,
                    "dbid": avatar.databaseID,
                    "offical": avatar.officalPosition,
                    "level": avatar.level,
                    "power": power,
                    "playerMB":playerMB
                }
                isJoin = False
                # 移除申请信息
                if avatar.guildDBID > 0:
                    for item in self.applyMember:
                        if applyerDBID == applyerDBID:
                            self.applyMember.remove(item)
                            isJoin=True
                            break

                # 已经在线了(异步调用)
                if wasActive:
                    if isJoin == True :
                        return
                    argMap = {
                        "guildMB"   : self,
                        "guildDBID" : self.databaseID,
                        "power": power,
                    }
                    param["onlineState"] = 1
                    avatar.onPlayerMgrCmd("setGuildDBID",argMap)
                else:
                    if isJoin == False:
                        avatar.guildDBID = self.databaseID
                        avatar.guildPower = power
                        avatar.applyGuildList=[]
                        param["onlineState"] = avatar.logoutTime
                    avatar.destroy()

                if isJoin == False:
                    self.onJoinGuildCB(param)


            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")
        KBEngine.createBaseFromDBID("Avatar",applyerDBID,agreeJoinCB)


    def onJoinGuildCB(self,argMap):
        # 加入成功
        applyerDBID = argMap["dbid"]

        # 移除申请信息
        for item in self.applyMember:
            if applyerDBID == item["dbid"]:
                self.applyMember.remove(item)
                self.getGuildApplyList(argMap["playerMB"])
                break

        # 判断是否曾经加入过
        for item in self.leaveGuildMember:
            if item["dbid"] == applyerDBID:
                item["power"] = argMap["power"]
                item["offical"] = argMap["offical"]
                item["level"] = argMap["level"]
                item["dayDonate"] = 0
                item["weekDonate"] = 0
                item["onlineState"] = argMap["onlineState"]

                break
        # 没有加入过。直接插入
        memberInfo = {
            "dbid"          : argMap["dbid"],
            "playerName"    : argMap["playerName"],
            "power"         : argMap["power"],
            "offical"       : argMap["offical"],
            "level"         : argMap["level"],
            "dayDonate"     :0,
            "weekDonate"    : 0,
            "sumDonate"     : 0,
            "onlineState"  : argMap["onlineState"]
        }
        self.guildMember.append(memberInfo)

        self.buildIndex()

        self.getGuildMemberList(argMap["playerMB"])

        param = {
            "guildDBID": self.databaseID,
            "count": len(self.guildMember)
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdRefreshGuildCount",param)

        def onLookUpCB(applyerAvatar):
            # 在线
            if type(applyerAvatar) is not bool:
                applyerAvatar.client.onResponse(GuildNotice.GuildNotice.guild_jion_success)
                self.onCreateGuildBuild()
                param = {"playerMB": applyerAvatar}
                self.getGuildInfo(param)

        KBEngine.lookUpBaseByDBID("Avatar",applyerDBID,onLookUpCB)


    # 拒绝加入申请
    def rejectApply(self,argMap):

        applyerDBID = argMap["applyerDBID"]
        playerMB = argMap["playerMB"]
        for item in self.applyMember:
            if item["dbid"] == applyerDBID:
                self.applyMember.remove(item)

                def checkApplyer(avatar, dbid, wasActive):
                    if avatar != None:
                        param={
                            "guildDBID": self.databaseID,
                        }
                        if wasActive:
                            avatar.onPlayerMgrCmd("setApplyGuildDBIDList", param)

                        else:
                            for guildId in avatar.applyGuildList:
                                if guildId == self.databaseID:
                                    avatar.applyGuildList.remove(guildId)
                            avatar.destroy()

                self.getGuildApplyList(playerMB)
                KBEngine.createBaseFromDBID("Avatar", applyerDBID, checkApplyer)

                return


    # 创建公会建筑
    def onCreateGuildBuild(self):

        for id,build in GuildBuildConfig.items():
            ERROR_MSG("--GuildBuildConfig--" + str(id))
            buildParam = {}
            buildParam["id"] = build["id"]
            buildParam["level"] = build["level"]
            buildParam["endTime"] = 0
            buildParam["state"] = 0
            self.guildBuild.append(buildParam)

        self.creatBuildBDIndex()


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
        isIntro =argMap["isIntro"]
        introduce =argMap["introduce"]
        isNotice =argMap["isNotice"]
        notice =argMap["notice"]
        selfDBID = argMap["selfDBID"]

        # 检查权限
        if  selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]

        selfPower = myItem["power"]
        changePower = guildConfig.PowerConfig[selfPower]["editNotice"]
        if changePower != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        if isIntro == 1:
            self.introduction = introduce
        if isNotice == 1:
            self.notice = notice

        playerMB.client.onResponse(GuildNotice.GuildNotice.change_notice_success)
        playerMB.client.onChangeNoticeSucc(self.notice,self.introduction)

    # 申请数据是否存在
    def isExitApplyInfo(self,applyID):
        isexit = 0
        for applyItem in self.applyMember:
            if applyItem["dbid"] == applyID:
                isexit = 1
                break

        return isexit

    # 修改公会名字
    def changeGuildName(self,argMap):
        guildName = argMap["guildName"]
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        # 检查权限
        if  selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]

        selfPower = myItem["power"]

        if selfPower != PowerEnmu.leader:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        self.name =guildName
        # 刷新列表公会名字
        param = {
            "guildDBID": self.databaseID,
            "guildName": guildName
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("refreshGuildName",param)

        playerMB.client.onChangeNameSucc(self.name)



    def kickOut(self,argMap):
        playerDBID = argMap["playerDBID"]
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        # 检查权限
        if playerDBID not in self.dbidToIndex or selfDBID not in self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_in_guild)
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

        param = {
            "guildDBID": self.databaseID,
            "count": len(self.guildMember)
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdRefreshGuildCount", param)


        def kictOutSucc(avatar, dbid, wasActive):
            if avatar != None:
                # 已经在线了(异步调用)
                if wasActive:
                    argMap = {
                        "guildDBID": 0,
                        "power": 0,
                        "guildShopLevel":0,
                        "guildName":''
                    }
                    avatar.onPlayerMgrCmd("setGuildDBID", argMap)
                    avatar.client.onResponse(GuildNotice.GuildNotice.guild_kick_success)
                else:
                    avatar.guildPower = 0
                    avatar.guildDBID = 0
                    avatar.guildShopLevel=0
                    avatar.guildName = ''
                    avatar.destroy()
                playerMB.client.onResponse(GuildNotice.GuildNotice.guild_kick_success)


            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")

        KBEngine.createBaseFromDBID("Avatar", playerDBID, kictOutSucc)
        playerMB.client.onKictOutSucc(playerDBID)

    # 退出公会
    def quitGuild(self,argMap):
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        # 检查
        if selfDBID not in self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_has_not_join)
            return

        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        self.guildMember.remove(myItem)
        self.buildIndex()

        playerMB.guildDBID = 0
        playerMB.guildPower = 0
        playerMB.guildShopLevel = 0
        playerMB.guildName = ''

        param = {
            "guildDBID": self.databaseID,
            "count": len(self.guildMember)
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdRefreshGuildCount", param)

        playerMB.client.onResponse(GuildNotice.GuildNotice.guild_quit_success)



    # 公会任命
    def appoinPower(self,argMap):

        playerDBID = argMap["playerDBID"]
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        power = argMap["power"]
        # 检查权限
        if playerDBID not in self.dbidToIndex or selfDBID not in self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_in_guild)
            return

        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        memberItem = self.guildMember[self.dbidToIndex[playerDBID]]

        selfPower = myItem["power"]
        memberPower = memberItem["power"]

        selfJunior= guildConfig.PowerConfig[selfPower]["junior"]


        if selfPower <= power or selfPower <= memberPower or selfJunior != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        #  判断职务人数是否满足
        powerNum =  guildConfig.PowerConfig[power]["num"]
        if powerNum > 0 :
            hasNum = self.guildPowerNum(power)
            if hasNum >= powerNum :
                playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
                return

        memberItem["power"] = power

        playerMB.client.onGuilRefreshMemeber(memberItem)

        def appoinPowerSucc(avatar, dbid, wasActive):
            if avatar != None:
                # 已经在线了(异步调用)
                ERROR_MSG("--appoinPowerSucc-wasActive-" + str(power))

                if wasActive:
                    argMap = {
                        "guildDBID": self.databaseID,
                        "power": power,
                    }
                    ERROR_MSG("--appoinPowerSucc--"+str(power))

                    avatar.onPlayerMgrCmd("setGuildDBID", argMap)

                else:
                    avatar.guildPower = power
                    avatar.destroy()

                playerMB.client.onResponse(GuildNotice.GuildNotice.appoin_power)


            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")

        KBEngine.createBaseFromDBID("Avatar", playerDBID, appoinPowerSucc)


    # 公会转让
    def guildTransfer(self,argMap):

        playerDBID = argMap["playerDBID"]
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]
        # 检查权限
        if playerDBID not in self.dbidToIndex or selfDBID not in self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_in_guild)

            return

        memberItem = self.guildMember[self.dbidToIndex[playerDBID]]

        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        selfPower = myItem["power"]

        if selfPower != PowerEnmu.leader :
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        memberItem["power"] =  PowerEnmu.leader
        myItem["power"] = PowerEnmu.member
        playerMB.client.onGuilRefreshMemeber(memberItem)
        playerMB.client.onGuilRefreshMemeber(myItem)
        playerMB.guildPower = PowerEnmu.member

        def transferSucc(avatar, dbid, wasActive):
            if avatar != None:
                # 已经在线了(异步调用)
                if wasActive:
                    argMap = {
                        "guildDBID": self.databaseID,
                        "power": PowerEnmu.leader,
                    }
                    avatar.onPlayerMgrCmd("setGuildDBID", argMap)

                    avatar.client.onResponse(GuildNotice.GuildNotice.guild_transfer_success)

                else:
                    avatar.guildPower = PowerEnmu.leader
                    avatar.destroy()

                playerMB.client.onResponse(GuildNotice.GuildNotice.guild_transfer_success)
                # 刷新会长
                argMap = {
                    "guildDBID": self.databaseID,
                    "leader": avatar.name
                }
                guildMgr = KBEngine.globalData["GuildMgr"]
                guildMgr.onCmd("refreshGuildLeader", argMap)

            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")

        KBEngine.createBaseFromDBID("Avatar", playerDBID, transferSucc)


    #     得到公会该职务数量

    def guildPowerNum(self,power):
        hasNum = 0
        for member in self.guildMember:
            if member["power"] == power:
                hasNum = hasNum + 1

        return hasNum


    def onChangeOnlineState(self,argMap):
        playerDBID = argMap[ "playerDBID"]
        onlineState = argMap["onlineState"]
        if playerDBID not in self.dbidToIndex:
            return
        index = self.dbidToIndex[playerDBID]

        item = self.guildMember[index]

        item["onlineState"] = onlineState

    # 公会上诉曝光
    def guildAppealExposure(self,argMap):

        appeadID = argMap["appeadID"]
        playerMB = argMap["playerMB"]

        isProtect = guildAppealConfig.GuildAppealConfig[appeadID]["isProtect"]

        # 能否保护
        if isProtect==1 and self.protectTime > 0:
            playerMB.client.onGuildError(GuildModuleError.Guild_is_by_prtected)
            return

        # 判断道具是否满足
        material = guildAppealConfig.GuildAppealConfig[appeadID]["material"]
        for itemId, num in material.items():
            have = playerMB.getItemNumByItemID(itemId)
            if have < num:
                ERROR_MSG(
                    "--------- num bu zu------- have   " + str(have) + "   need  " + str(num) + "   " + str(itemId))
                playerMB.client.onGuildError(GuildModuleError.Guild_appeal_not_enough)
                return

        for itemId, num in material.items():
            playerMB.decItem(itemId, num)

        subFunds = guildAppealConfig.GuildAppealConfig[appeadID]["subGuildFunds"]
        subReputation = guildAppealConfig.GuildAppealConfig[appeadID]["subReputation"]
        rewardDonate = guildAppealConfig.GuildAppealConfig[appeadID]["rewardDonate"]

        # 概率判断
        succProb = guildAppealConfig.GuildAppealConfig[appeadID]["succProb"]
        ran_num = random.randint(0, 100)
        ERROR_MSG("---guildAppealExposure--ran_num-"+str(ran_num))
        if ran_num > succProb :
            playerMB.client.onGuildError(GuildModuleError.Guild_appeal_fail)
            return

        if  self.guildFunds - subFunds>0:
            self.guildFunds = self.guildFunds - subFunds
        else:
            self.guildFunds =0

        if self.reputation - subReputation > 0:
            self.reputation = self.reputation - subReputation
        else:
            self.reputation = 0


        playerMB.guildDonate = playerMB.guildDonate + rewardDonate
        playerMB.client.onResponse(GuildNotice.GuildNotice.guild_appealExposure_success)


    # 购买保护时间
    def guildBuyProtect(self,argMap):

        hour = argMap["hour"]
        playerMB = argMap["playerMB"]

        self.protectTime = self.protectTime + hour*60*60

        playerMB.client.onBuyGuildProtectSucc(self.protectTime)
        pass


     # 弹劾
    def impeach(self,argMap):
        playerMB = argMap["playerMB"]

        selfDBID = argMap["selfDBID"]
        # 检查自己的权限
        if selfDBID not in self.dbidToIndex:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_in_guild)

            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        selfPower = myItem["power"]
        selfCanImpeach= guildConfig.PowerConfig[selfPower]["impeach"]

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

    #  公会解散
    def dismissGuild(self,argMap):
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]

        # 检查自己的权限
        if selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        selfPower = myItem["power"]

        if selfPower != PowerEnmu.leader :
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        dissTime = guildConfig.GuildConfig[1]["dismissTime"]*24*60*60 + util.getCurrentTime()

        self.dismissTime = dissTime
        playerMB.client.onResponse(GuildNotice.GuildNotice.guild_dismiss_success)
        playerMB.client.onGuildReadyDismiss(dissTime)

        pass
    # 取消解散公会
    def cancelDismiss(self,argMap):
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        # 检查自己的权限
        if selfDBID not in self.dbidToIndex:
            return
        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        selfPower = myItem["power"]
        if selfPower != PowerEnmu.leader:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        self.dismissTime = 0
        playerMB.client.onResponse(GuildNotice.GuildNotice.guild_cancel_dismiss_success)


    # 建筑升级
    def guildBuildUpgrade(self,argMap):

        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        buildID = argMap["buildID"]

        # 检查权限
        if selfDBID not in self.dbidToIndex:
            return


        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        # 权限判断
        selfPower = myItem["power"]
        selfCanUpgradeBuild = guildConfig.PowerConfig[selfPower]["upgradeBuild"]
        if selfCanUpgradeBuild != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        buildData =  self.guildBuild[self.buildBDToIndex[buildID]]

        # 判断公会等级
        buildLevel = buildData["level"]

        if buildLevel >= self.level :
            playerMB.client.onGuildError(GuildModuleError.Guild_level_not_enough)
            return

        # 正在升级
        if  buildData["state"] == 1:
            return


        maxLevel = guildConfig.GuildConfig[1]["maxLevel"]
        if buildLevel >= maxLevel :
            return

        buildInfo = self.buildConfigInfo(buildID,buildLevel)

        if self.guildFunds < buildInfo["needFunds"] :
            playerMB.client.onGuildError(GuildModuleError.Guild_guildFunds_not_enough)
            return

        buildData["state"] = 1
        self.guildFunds = self.guildFunds -  buildInfo["needFunds"]

        endTime = util.getCurrentTime() + buildInfo["needTime"]*60*60
        buildData["endTime"] = endTime
        playerMB.client.onClientGuildBuildInfo(buildData)


    # 检查公会解散时间
    def checkGuildDismiss(self,argMap):
        playerMB = argMap["playerMB"]
        selfDBID = argMap["selfDBID"]

        if self.dismissTime <= 0:
            return

        if util.getCurrentTime() < self.dismissTime:
            return

        self.dismissTime = 0;

        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("dismissGuild", self.databaseID)


        for member in self.guildMember:
            playerDBID  = member["dbid"]
            def dismissSucc(avatar, dbid, wasActive):
                if avatar != None:
                    # 已经在线了(异步调用)
                    if wasActive:
                        argMap = {
                            "guildDBID": 0,
                            "power": 0,
                        }
                        avatar.onPlayerMgrCmd("setGuildDBID", argMap)
                    else:
                        avatar.guildDBID = 0
                        avatar.guildPower = 0
                        avatar.destroy()
                    avatar.client.onResponse(GuildNotice.GuildNotice.guild_dismiss_success)
                else:
                    ERROR_MSG("---------Cannot add unknown player:-------------")

            KBEngine.createBaseFromDBID("Avatar", playerDBID, dismissSucc)


    # 获取公会最大成员数量

    def guildMaxMember(self):
        maxMemberCount = guildConfig.GuildConfig[1]["maxMemberNum"]
        if BuildEnmu.Hall in self.buildBDToIndex:
            buildData = self.guildBuild[self.buildBDToIndex[BuildEnmu.Hall]]
            buildHallConfig = self.buildConfigInfo(BuildEnmu.Hall, buildData["level"])
            maxMemberCount = maxMemberCount + buildHallConfig["addNum"]
        return  maxMemberCount



    # 建筑升级检查
    def guildCheckBuildUpgrade(self,argMap):

        playerMB = argMap["playerMB"]

        for build in self.guildBuild :
            if build["state"] == 1 :
                endTime = build["endTime"]
                leftTime = endTime - util.getCurrentTime()
                if util.getCurrentTime() >= endTime :

                    build["level"] =  build["level"] + 1
                    build["state"] = 0
                    build["endTime"] = 0
                    playerMB.guildShopLevel = build["level"]
                    playerMB.client.onClientGuildBuildInfo(build)
        pass

    # 检查公会保护时间
    def checkProtectTime(self,argMap):
        playerMB = argMap["playerMB"]

        if self.protectTime <= 0:
            return
        if  self.protectTime > 0:
            self.protectTime = self.protectTime - 60

        if self.protectTime <= 0 :
            self.protectTime = 0

        playerMB.client.onBuyGuildProtectSucc(self.protectTime)


    # 获取建筑配置信息
    def buildConfigInfo(self,buildID,level):

        if buildID == BuildEnmu.Hall:
            return  guildUpHallConfig.GuildUpHallConfig[level]
        elif buildID == BuildEnmu.Shop:
            return guildUpShopConfig.GuildUpShopConfig[level]
        elif buildID == BuildEnmu.Consultant:
            return guildUpCouConfig.GuildUpCouConfig[level]
        elif buildID == BuildEnmu.Task:
            return guildUpTaskConfig.GuildUpTaskConfig[level]

        return None

    # 建筑升级加速
    def guildBuildSpeed(self,argMap):

        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        buildID = argMap["buildID"]
        speedHour = argMap["speedHour"]

        # 检查权限
        if selfDBID not in self.dbidToIndex:
            return

        myItem = self.guildMember[self.dbidToIndex[selfDBID]]
        # 权限判断
        selfPower = myItem["power"]
        selfCanUpgradeBuild = guildConfig.PowerConfig[selfPower]["upgradeBuild"]
        if selfCanUpgradeBuild != 1:
            playerMB.client.onGuildError(GuildModuleError.Guild_not_has_the_power)
            return

        buildData =  self.guildBuild[self.buildBDToIndex[buildID]]
        if  buildData["state"] == 0 :
            return

        needFunds = speedHour * guildConfig.GuildConfig[1]["speedTimeFunds"]

        if self.guildFunds < needFunds :
            playerMB.client.onGuildError(GuildModuleError.Guild_guildFunds_not_enough)
            return

        self.guildFunds = self.guildFunds - needFunds

        endTime = buildData["endTime"] - speedHour*60*60
        leftTime = endTime - util.getCurrentTime()

        if leftTime > 0:
            buildData["endTime"] = endTime
        else:
            buildData["level"] = buildData["level"] + 1
            buildData["state"] = 0
            buildData["endTime"] = 0
            playerMB.guildShopLevel = buildData["level"]

        playerMB.client.onClientGuildBuildInfo(buildData)
        playerMB.client.onClientGuildFunds(self.guildFunds)


    def updateGuildValueRank(self):
        param = {
            "dbid": self.databaseID,
            "guildName": self.name,
            "camp": self.camp,
            "level": self.level,
            "leader": self.leader,
            "reputation": self.reputation,
            "guildFunds" :self.guildFunds,
        }
        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateGuildValueRank", param)



    # 清除公会成员周贡献
    def clearWeekDonate(self):
        for member in self.guildMember:
            member["weekDonate"] = 0


    # 清除公会成员日贡献
    def clearDayDonate(self):
        for member in self.guildMember:
            member["dayDonate"] = 0

    # 公会捐钱
    def guildDonate(self,argMap):
        selfDBID = argMap["selfDBID"]
        playerMB = argMap["playerMB"]
        euro = argMap["euro"]
        donate = argMap["donate"]

        if selfDBID not in self.dbidToIndex:
            return
        playerMB.euro =  playerMB.euro - euro
        playerMB.guildDonate = playerMB.guildDonate + donate
        self.guildFunds = self.guildFunds + euro

        index = self.dbidToIndex[selfDBID]
        member = self.guildMember[index]

        member["dayDonate"] = member["dayDonate"] + euro
        member["weekDonate"] = member["weekDonate"] + euro
        member["sumDonate"] = member["sumDonate"] + euro

        # playerMB.client.onResponse(GuildNotice.GuildNotice.donate_success)
        playerMB.client.onGuildDonateSucc(self.guildFunds,member)

        for item in self.guildMember:
            playerID = item["dbid"]
            def onLookUpCB(applyerAvatar):
                # 在线
                if type(applyerAvatar) is not bool:
                    applyerAvatar.client.onGuildDonateSucc(self.guildFunds,item)


            KBEngine.lookUpBaseByDBID("Avatar", playerID, onLookUpCB)





    # 公会升级
    def guiildUpdate(self,argMap):

        playerMB = argMap["playerMB"]
        level = self.level
        maxLevel = guildConfig.GuildConfig[1]["maxLevel"]
        if level >= maxLevel:
            return

        guildUpgrade = GuildUpgradeConfig[level]
        needReputation = guildUpgrade["needReputation"]

        if self.reputation < needReputation :
            return

        while(self.reputation >= needReputation and self.level < maxLevel) :
            self.reputation = self.reputation - guildUpgrade["needReputation"]
            self.level = self.level + 1
            guildUpgrade = GuildUpgradeConfig[level]
            needReputation = guildUpgrade["needReputation"]

        playerMB.client.onGuildUpgradeSucc(self.level,self.reputation)
      # 刷新列表公会名字
        param = {
            "guildDBID": self.databaseID,
            "level": self.level
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("refreshGuildLevel",param)





    # GM增加公会资金
    def addGuildFunds(self,argMap):
        funds = argMap["funds"]
        self.guildFunds = self.guildFunds + funds
        ERROR_MSG("--addGuildFunds--"+str( self.guildFunds))
        # GM增加公会资金

    # GM增加公会声望
    def addGuildReputation(self, argMap):
        reputation = argMap["reputation"]
        self.reputation = self.reputation + reputation
        ERROR_MSG("--addGuildFunds--" + str(self.reputation))

        self.guiildUpdate(argMap)

    # 重建索引
    def buildIndex(self):
        self.dbidToIndex = {}
        for index in range(len(self.guildMember)):
            dbid = self.guildMember[index]["dbid"]
            self.dbidToIndex[dbid] = index


    def creatBuildBDIndex(self):
        self.buildBDToIndex = {}
        for index in range(len(self.guildBuild)):
            dbid = self.guildBuild[index]["id"]
            self.buildBDToIndex[dbid] = index






