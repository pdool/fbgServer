# -*- coding: utf-8 -*-
import datetime
import random

import CommonConfig
import KBEngine
import TimerDefine
import cloneConfig
import officialConfig
import officialPermissionConfig
import util
import cardLevelUpgradeConfig
import vipConfig
from CommonEnum import ActionTypeEnum
from ErrorCode import OfficialModulerror, CloneModuleError
from part.GameShopModule import Euro_type, ERROR_MSG, Diamond_type

__author__ = 'yangh'
"""
充钱花钱
"""
Get_Friend = 0
Get_Guild = 1
Get_Others = 2
Get_Black = 3

Zutangshengyan = 1 # 足坛盛宴
Jinsai = 2         # 禁赛
Jinyan = 3         # 禁言
Tingsai = 4        # 停赛
Baohu = 5          # 保护
Tiba = 6           # 提拔
Xiaheijiao = 7     # 下黑脚
Diubaicai = 8      # 丢白菜
Rengjidan = 9      # 扔鸡蛋
Zhangzui = 10      # 掌嘴
Feichu = 11        # 废除
Huibao = 12        # 汇报
Gudashou = 13      # 雇打手
Baifang = 14       # 拜访
Tiaozhan = 15      # 挑战
huifang = 16       # 回访


class OfficialModule:
    def __init__(self):
        self.roomMB = None

    def onEntitiesEnabled(self):
        config = officialPermissionConfig.officialPermissionConfig
        if len(self.permissionInfoList) == 0:
            for id in config:
                limitItem = {}
                item = {}
                item["officialId"] = 0
                item["id"] = id
                item["haveTimes"] = config[id]["haveTimes"][self.officialPosition - 1]
                item["useTimes"] = item["haveTimes"]
                item["type"] = config[id]["type"]
                limitItem["itemID"] = id
                limitItem["number"] = 0
                self.permissionInfoList.append(item)
                self.useTopLimitList.append(limitItem)

        offset = util.getLeftSecsToNextHMS(0, 0, 0)
        self.addTimer(offset, 24 * 60 * 60, TimerDefine.Time_update_permission_times)

        #  离上次下线多长时间
        period =  util.getCurrentTime() - self.logoutTime

        #  刷新行动力
        power = int(period / (2 * 60 * 60))
        if self.linePower + power > 6:
            self.linePower = 6
        else:
            self.linePower += power

        offset = 2 * 60 * 60 - period % (2 * 60 * 60)

        self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_update_linePower)

    # 被其他玩家使用了权限 初始化状态
    def initialPermissionInfo(self):
        #  判断有没有球员被禁赛
        if self.suspensionBallerId != 0:
            period = util.getCurrentTime() - self.suspensionOutTime
            if period >= 0.5 * 60 * 60:
                for item in self.cardConfigIdList:
                    if item["configID"] == self.suspensionBallerId:
                        self.inTeamcardIDList.append(item["id"])
                        break
                self.suspensionBallerId = 0
                self.Time_suspensionBallerId = 0
            else:
                offset = 0.5 * 60 * 60 - period
                self.Time_suspensionBallerId = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_suspensionBallerId)
        #  判断有没有被禁言
            if self.Time_suspensionTalkId != 0:
                period = util.getCurrentTime() - self.suspensionTalkOutTime
                if period >= 600:
                    self.Time_suspensionTalkId = 0
                else:
                    offset = 600 - period
                self.Time_suspensionTalkId = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_suspensionTalkId)

        #  判断有没有被保护
            if self.isProtected != 0:
                period = util.getCurrentTime() - self.isProtectedOutTime
                if period >= 3600:
                    self.isProtected = 0
                else:
                    offset = 3600 - period
                self.Time_isProtected = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_isProtected)

        #  判断有没有被下黑脚
        if self.isBeBlackFoot != 0:
            period = util.getCurrentTime() - self.isBeBlackFootOutTime
            if period >= 600:
                self.SetObjectValue(self.cardID, "controll",
                                    self.controllDownValue + self.GetObjectValue(self.cardID, "controll"))
                self.controllDownValue = 0
                self.isBeBlackFoot = 0
            else:
                if self.controllDownValue == 0:
                    self.reduceBallerInfoByOfficial("controll")
                offset = 600 - period
                self.Time_isBeBlackFoot = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_isBeBlackFoot)

        #  判断有没有被丢白菜
        if self.isCabbage != 0:
            period = util.getCurrentTime() - self.isCabbageOutTime
            if period >= 600:
                addValue = self.GetObjectValue(self.cardID, "defend")
                self.SetObjectValue(self.cardID, "defend",
                                    self.defendDownValue + addValue)
                self.defendDownValue = 0
                self.isCabbage = 0
            else:
                if self.defendDownValue == 0:
                    self.reduceBallerInfoByOfficial("defend")
                offset = 600 - period
                self.Time_isCabbage = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_isCabbage)

        #  判断有没有被丢鸡蛋
        if self.isThrowEggs != 0:
            period = util.getCurrentTime() - self.isThrowEggsOutTime
            if period >= 600:
                self.SetObjectValue(self.cardID, "shoot",
                                    self.shootDownValue + self.GetObjectValue(self.cardID, "shoot"))
                self.shootDownValue = 0
                self.isThrowEggs = 0
            else:
                if self.shootDownValue == 0:
                    self.reduceBallerInfoByOfficial("shoot")
                offset = 600 - period
                self.Time_isThrowEggs = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_isThrowEggs)

        #  判断有没有被掌嘴
        if self.isStuttering != 0:
            period = util.getCurrentTime() - self.isStutteringOutTime
            if period >= 600:
                self.isStuttering = 0
            else:
                offset = 600 - period
                self.Time_isStuttering = self.addTimer(offset, 2 * 60 * 60, TimerDefine.Time_isStuttering)

    #  玩家下线
    def onClientDeath(self):
        self.suspensionOutTime = util.getCurrentTime()
        self.suspensionTalkOutTime = util.getCurrentTime()
        self.isProtectedOutTime = util.getCurrentTime()
        self.isBeBlackFootOutTime = util.getCurrentTime()
        self.isCabbageOutTime = util.getCurrentTime()
        self.isThrowEggsOutTime = util.getCurrentTime()
        self.isStutteringOutTime = util.getCurrentTime()
    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def onTimer(self, id, userArg):
        # 行动力
        if userArg == TimerDefine.Time_update_linePower:
            if self.linePower + 1 > 6:
                self.linePower = 6
            else:
                self.linePower += 1
        # 禁赛时间到
        elif userArg == TimerDefine.Time_suspensionBallerId:
            self.suspensionBallerId = 0
            self.Time_suspensionBallerId = 0
            self.delTimer(id)
        # 禁言时间到
        elif userArg == TimerDefine.Time_suspensionTalkId:
            self.Time_suspensionTalkId = 0
            self.delTimer(id)
        # 保护时间到
        elif userArg == TimerDefine.Time_isProtected:
            self.isProtected = 0
            self.Time_isProtected = 0
            self.delTimer(id)
        # 下黑脚时间到
        elif userArg == TimerDefine.Time_isBeBlackFoot:
            self.isBeBlackFoot = 0
            self.Time_isBeBlackFoot = 0
            self.SetObjectValue(self.cardID, "controll", self.controllDownValue + self.GetObjectValue(self.cardID, "controll"))
            self.controllDownValue = 0
            self.delTimer(id)
        # 丢白菜时间到
        elif userArg == TimerDefine.Time_isCabbage:
            self.isCabbage = 0
            self.Time_isCabbage = 0
            self.SetObjectValue(self.cardID, "defend",
                                self.defendDownValue + self.GetObjectValue(self.cardID, "defend"))
            self.defendDownValue = 0
            self.delTimer(id)
        # 丢鸡蛋时间到
        elif userArg == TimerDefine.Time_isThrowEggs:
            self.isThrowEggs = 0
            self.Time_isThrowEggs = 0
            self.SetObjectValue(self.cardID, "shoot",
                                self.shootDownValue + self.GetObjectValue(self.cardID, "shoot"))
            self.shootDownValue = 0
            self.delTimer(id)
        # 掌嘴时间到
        elif userArg == TimerDefine.Time_isStuttering:
            self.isStuttering = 0
            self.Time_isStuttering = 0
            self.delTimer(id)
        # 刷新权限次数
        elif userArg == TimerDefine.Time_update_permission_times:
            self.usePlayerDbidList = []
            self.updateforPermissionInfo()

    # 刷新权限次数
    def updateforPermissionInfo(self):
        for item in self.permissionInfoList:
            if item["type"] == 2:
                item["useTimes"] = 0

    # 更新玩家官职信息
    def onResertPlayerOfficial(self,officialID,avatar = None):
        if avatar != None:
            playerMb = avatar
        else:
            playerMb = self

        if playerMb.officialPosition == officialID:
            return
        playerMb.onUpdatePermissionInfo(officialID,playerMb)
        playerMb.officialPosition = officialID
        if playerMb.maxOffical < officialID:
            playerMb.maxOffical = officialID

    # 是否在足坛盛宴期间
    def judgeInFootBallFeast(self,avatarAID,aScore,avatarBID,bScore):
        officialMgr = KBEngine.globalData["OfficialMgr"]
        param = {
            "dbid": self.databaseID,
            "avatarAID": avatarAID,
            "aScore": aScore,
            "avatarBID": avatarBID,
            "bScore": bScore,
        }
        officialMgr.onCmd("onCmdJudgeInFootBallFeast", param)

    # 是否在足坛盛宴期间
    def getIsInFootBallFeast(self,param):
        footBallFeast = param["footBallFeast"]
        avatarAID = param["avatarAID"]
        aScore = param["aScore"]
        avatarBID = param["avatarBID"]
        bScore = param["bScore"]
        self.onCloneRoomEndResult(avatarAID, aScore, avatarBID, bScore,footBallFeast)

    # 对玩家使用权限
    def onClientUsePrmissionInfo(self,playerID,permissionInfoID):
        permissionFindItem = None
        for item in self.permissionInfoList:
            if item["id"] == permissionInfoID:
                if item["useTimes"] <= 0:
                    self.client.signUpCallBack(OfficialModulerror.prmissionInfo_not_times)
                    return
                permissionFindItem = item
                break
        if permissionInfoID == Zutangshengyan:
            self.usePrmissionInfo1(permissionInfoID,permissionFindItem)
        elif permissionInfoID == huifang:
            # 对在线的玩家可使用，获得5000欧元
            self.euro += 5000
        else:
            if permissionInfoID == Baifang:
                if self.delMoneyByType(Euro_type, 5000) is False:
                    return

            param = {
                "playerMB": self,
                "usePlayerDbidList": self.usePlayerDbidList,
                "permissionInfoList": self.permissionInfoList,
                "databaseID": self.databaseID,
                "name": self.name,
                "photoIndex": self.photoIndex,
                "playerID": playerID,
                "permissionInfoID": permissionInfoID,
            }
            KBEngine.globalData["PlayerMgr"].getPlayerUsePrmissionInfo(param)


    # 开启后，全服所有玩家在精英副本、普通副本获得双倍经验，持续1小时
    def usePrmissionInfo1(self,permissionInfoID,permissionFindItem):
        param = {
        }
        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdOpenFootBallFeast", param)
        permissionFindItem["useTimes"] -= 1
        self.client.usePrmissionSucess(permissionInfoID)

    # 可对比自己官职低的玩家使用，被使用者将会有一名除主角外的在阵球员被禁赛，半小时内无法参与任何比赛
    def usePrmissionInfo2(self,param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        index = 0
        findItem = None
        for item in avatar.cardConfigIdList:
            index += 1
            if index == 4:
                findItem = item
                avatar.suspensionBallerId = item["configID"]
                avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                                     permissionInfoID,
                                     0, 1, 1,0,0,avatar.suspensionBallerId)
                break
        if wasActive == 0:
            avatar.suspensionOutTime = util.getCurrentTime()
        else:
            for id in avatar.inTeamcardIDList:
                if findItem["id"] == id:
                    avatar.inTeamcardIDList.remove(id)

            if avatar.Time_suspensionBallerId != 0:
                if avatar.Time_suspensionBallerId != 0:
                    avatar.delTimer(avatar.Time_suspensionBallerId)
                avatar.Time_suspensionBallerId = avatar.addTimer(0.5 * 60 * 60, 2 * 60 * 60,
                                                              TimerDefine.Time_suspensionBallerId)

        self.usePrmissionOver(playerMB,avatar,permissionInfoID,playerID,usePlayerDbidList,useTopLimit,wasActive,permissionInfoList)

    # 禁言
    def usePrmissionInfo3(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)
        if wasActive == 0:
            avatar.Time_suspensionTalkId = 1
            avatar.suspensionTalkOutTime = util.getCurrentTime()
        else:
            if avatar.Time_suspensionTalkId != 0:
                avatar.delTimer(avatar.Time_suspensionTalkId)
            avatar.Time_suspensionTalkId = avatar.addTimer(600, 2 * 60 * 60, TimerDefine.Time_suspensionTalkId)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 可对比自己官职低的玩家使用，被使用者将会有一名除主角外的在阵球员被停赛1场联赛比赛
    def usePrmissionInfo4(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        index = 0
        findItem = None
        for item in avatar.cardConfigIdList:
            index += 1
            if index == 4:
                findItem = item
                avatar.notMatchBallerID = item["configID"]
                avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                                     permissionInfoID,
                                     0, 1, 1, 0, 0, avatar.notMatchBallerID)
                break
        if wasActive == 1:
            for id in avatar.inTeamcardIDList:
                if findItem["id"] == id:
                    avatar.inTeamcardIDList.remove(id)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)


    # 可对低于自己官品的玩家使用，使用后立即解除并保护玩家不受下黑脚、丢白菜、砸鸡蛋、掌嘴、雇打手影响，持续1小时
    def usePrmissionInfo5(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        avatar.isProtected = 1
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 2, 1)
        if wasActive == 0:
            avatar.isProtectedOutTime = util.getCurrentTime()
        else:
            if avatar.Time_isProtected != 0:
                avatar.delTimer(avatar.Time_isProtected)
            avatar.Time_isProtected = avatar.addTimer(3600, 2 * 60 * 60, TimerDefine.Time_isProtected)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 可提拔以太足理会理事（11号官品）以下的官品，消耗提拔次数1次，被提拔者官职直接升1阶
    def usePrmissionInfo6(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]

        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if avatar.officialPosition < 11:
            avatar.onResertPlayerOfficial(avatar.officialPosition + 1, avatar)
            avatar.updateOfficialValueRank(avatar.officialPosition, avatar)
            avatar.onRecordEvent(avatar, avatar.officialPosition, 0, databaseID, name, photoIndex,
                                 permissionInfoID,
                                 0, 2, 1)
        else:
            self.client.signUpCallBack(OfficialModulerror.official_cannot_up)
        if wasActive == 1 and avatar.officialPosition <= 11:
            avatar.client.upOfficialSucess(self.name, avatar.officialPosition)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 使用无限制，降低被使用者主角10%控球属性，持续10分钟
    def usePrmissionInfo7(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if avatar.isProtected == 1:
            if wasActive == 0:
                avatar.destroySelf()
            playerMB.client.signUpCallBack(OfficialModulerror.isProtected)
            return
        avatar.isBeBlackFoot = 1
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)
        if wasActive == 0:
            avatar.isBeBlackFootOutTime = util.getCurrentTime()
        else:
            if avatar.Time_isBeBlackFoot != 0:
                avatar.delTimer(avatar.Time_isBeBlackFoot)
            avatar.reduceBallerInfoByOfficial("controll", avatar)
            avatar.Time_isBeBlackFoot = avatar.addTimer(600, 2 * 60 * 60, TimerDefine.Time_isBeBlackFoot)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 使用无限制，降低被使用者主角10%防守属性，持续10分钟，同时该玩家头像挂上烂白菜
    def usePrmissionInfo8(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return

        if avatar.isProtected == 1:
            if wasActive == 0:
                avatar.destroySelf()
            playerMB.client.signUpCallBack(OfficialModulerror.isProtected)
            return
        avatar.isCabbage = 1
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)
        if wasActive == 0:
            avatar.isCabbageOutTime = util.getCurrentTime()
        else:
            if avatar.Time_isCabbage != 0:
                avatar.delTimer(avatar.Time_isCabbage)
            avatar.reduceBallerInfoByOfficial("defend", avatar)
            avatar.Time_isCabbage = avatar.addTimer(600, 2 * 60 * 60, TimerDefine.Time_isCabbage)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 使用无限制，降低被使用者主角10%射门属性，持续10分钟，同时该玩家头像上挂上臭鸡蛋
    def usePrmissionInfo9(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if avatar.isProtected == 1:
            if wasActive == 0:
                avatar.destroySelf()
            playerMB.client.signUpCallBack(OfficialModulerror.isProtected)
            return
        avatar.isThrowEggs = 1
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)
        if wasActive == 0:
            avatar.isThrowEggsOutTime = util.getCurrentTime()
        else:
            if avatar.Time_isThrowEggs != 0:
                avatar.delTimer(avatar.Time_isThrowEggs)
            avatar.reduceBallerInfoByOfficial("shoot", avatar)
            avatar.Time_isThrowEggs = avatar.addTimer(600, 2 * 60 * 60, TimerDefine.Time_isThrowEggs)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 对低于自己官职的玩家可使用，被使用的玩家聊天时特殊处理，持续10分钟
    def usePrmissionInfo10(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if avatar.isProtected == 1:
            if wasActive == 0:
                avatar.destroySelf()
            playerMB.client.signUpCallBack(OfficialModulerror.isProtected)
            return
        avatar.isStuttering = 1
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)
        if wasActive == 0:
            avatar.isStutteringOutTime = util.getCurrentTime()
        else:
            if avatar.Time_isStuttering != 0:
                avatar.delTimer(avatar.Time_isStuttering)
            avatar.Time_isStuttering = avatar.addTimer(600, 2 * 60 * 60, TimerDefine.Time_isStuttering)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)

    # 对不低于自己官品的玩家可使用，使用后增加自己所有卡牌的经验值
    def usePrmissionInfo12(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return

        KBEngine.globalData["PlayerMgr"].onGetCardLevelUp(databaseID)
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 2, 1)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit, wasActive,
                              permissionInfoList)


    def onCmdGetCardLevelUp(self,param):
        addCardExp = 0.5 * (self.level * self.level) + 2000
        for cardDBID in self.cardIDList:
            self.onCardLevelUp(cardDBID, addCardExp)
        self.client.signUpCallBack(int(addCardExp))


    # 对比自己低官品的玩家可使用，无实际效果
    # 傻逼策划  这个对玩家没任何作用 还要写 说显示下就行，真TM的傻逼
    def usePrmissionInfo13(self, param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if avatar.isProtected == 1:
            if wasActive == 0:
                avatar.destroySelf()
            playerMB.client.signUpCallBack(OfficialModulerror.isProtected)
            return
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 1, 1)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)

    # 对在线的玩家可使用，消耗5000欧元，获得5点体力
    def usePrmissionInfo14(self,param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        avatar.onRecordEvent(avatar, 0, 0, databaseID, name, photoIndex,
                             permissionInfoID,
                             0, 2, 1)
        KBEngine.globalData["PlayerMgr"].onAddPower(databaseID)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)


    # 挑战
    def usePrmissionInfo15(self,param):
        avatar = param["avatar"]
        databaseID = param["databaseID"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        fightValue = param["fightValue"]
        officialId = param["officialId"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]

        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return

        if fightValue > avatar.fightValue:
            sucessRate = (fightValue - avatar.fightValue) / 150
            if sucessRate >= 100:
                sucessRate = 100
        else:
            sucessRate = 100 - (avatar.fightValue - fightValue) / 150
            if sucessRate <= 0:
                sucessRate = 0

        count = random.randint(0, 100)
        if count <= sucessRate:
            officialMgr = KBEngine.globalData["OfficialMgr"]
            officialMgr.onCmd("onCmdUpdateOfficialRank", param)
            playerMB.client.signUpCallBack(OfficialModulerror.fight_sucess)
            return

        avatar.onRecordEvent(avatar, officialId, officialId, databaseID, name, photoIndex, 15, 0, 3, 0)
        playerMB.client.signUpCallBack(OfficialModulerror.fight_fail)
        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)

    # 废除
    def usePrmissionInfo11(self, param):
        avatar = param["avatar"]
        myOfficialId = param["myOfficialId"]
        name = param["name"]
        databaseID = param["databaseID"]
        photoIndex = param["photoIndex"]
        fightValue = param["fightValue"]
        officialId = param["officialId"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    if item["number"] >= useTopLimit:
                        playerMB.client.signUpCallBack(OfficialModulerror.useTopLimit)
                        return
        if fightValue > avatar.fightValue:
            sucessRate = (fightValue - avatar.fightValue) / 150
            if sucessRate >= 100:
                sucessRate = 100
        else:
            sucessRate = 100 - (avatar.fightValue - fightValue) / 150
            if sucessRate <= 0:
                sucessRate = 0

        count = random.randint(0, 100)
        if count <= sucessRate:
            officialMgr = KBEngine.globalData["OfficialMgr"]
            officialMgr.onCmd("onCmdAbolitionSucess", param)
            playerMB.client.signUpCallBack(OfficialModulerror.fight_sucess)
            return

        playerMB.client.signUpCallBack(OfficialModulerror.abolition_fail)
        avatar.onRecordEvent(avatar, myOfficialId, officialId, databaseID, name, photoIndex, 11, 0, 3, 0)
        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)

    # 废除成功
    def abolitionSucess(self, param):
        avatar = param["avatar"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        officialId = param["officialId"]
        databaseID = param["dbid"]
        myOfficialId = param["myOfficialId"]
        fame = param["fame"]
        nowFame = param["fame"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        avatar.onRecordEvent(avatar, myOfficialId, officialId, databaseID, name, photoIndex, 11, 0, 3, 1, fame,
                             nowFame)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)

    # 挑战成功
    def fightClleagues(self, param):
        avatar = param["avatar"]
        name = param["name"]
        photoIndex = param["photoIndex"]
        officialId = param["officialId"]
        databaseID = param["dbid"]
        clleaguesIndex = param["clleaguesIndex"]
        permissionInfoID = param["permissionInfoID"]
        wasActive = param["wasActive"]
        playerID = param["playerID"]
        playerMB = param["playerMB"]
        usePlayerDbidList = param["usePlayerDbidList"]
        permissionInfoList = param["permissionInfoList"]
        useTopLimit = param["useTopLimit"]
        avatar.onRecordEvent(avatar, officialId, officialId, databaseID, name, photoIndex, 15, clleaguesIndex + 1, 3,
                             1)
        if clleaguesIndex > 0:
            officialMgr = KBEngine.globalData["OfficialMgr"]
            officialMgr.onCmd("onCmdGetOfficialRankValue", param)

        self.usePrmissionOver(playerMB, avatar, permissionInfoID, playerID, usePlayerDbidList, useTopLimit,
                              wasActive,
                              permissionInfoList)


    def onCmdAddPower(self,param):
        self.bodyPower += 5

    # 权限使用成功
    def usePrmissionOver(self,playerMB,avatar,permissionInfoID,playerID,usePlayerDbidList,useTopLimit,wasActive,permissionInfoList):
        canRepeat = officialPermissionConfig.officialPermissionConfig[permissionInfoID]["canRepeat"]
        if canRepeat == 0 and permissionInfoID != 1:
            item = {}
            item["itemID"] = permissionInfoID
            item["number"] = playerID
            usePlayerDbidList.append(item)

        if useTopLimit != 0:
            for item in avatar.useTopLimitList:
                if item["itemID"] == permissionInfoID:
                    item["number"] += 1
                    break

        for item in permissionInfoList:
            if item["id"] == permissionInfoID:
                item["useTimes"] -= 1
                break

        if wasActive == 0:
            avatar.destroySelf()
        playerMB.client.usePrmissionSucess(permissionInfoID)


    # 记录事件
    def onRecordEvent(self,avatar,officialId,enmyOfficialId,enmyDbid, enmyName,photoIndex, id,rank,type,isSucess,fame = 0,nowFame = 0,ballerID = 0):
        eventInfo = {}
        eventInfo["eventId"] = id
        eventInfo["enmyDbid"] = enmyDbid
        eventInfo["enmyName"] = enmyName
        eventInfo["photoIndex"] = photoIndex
        eventInfo["eventType"] = type
        eventInfo["rank"] = rank
        eventInfo["isSucess"] = isSucess
        eventInfo["fame"] = fame
        eventInfo["nowFame"] = nowFame
        eventInfo["officialId"] = officialId
        eventInfo["enmyOfficialId"] = enmyOfficialId
        eventInfo["ballerID"] = ballerID
        if len(avatar.officialEventList) > 50:
            avatar.officialEventList.remove(avatar.officialEventList[50])
        avatar.officialEventList.insert(0, eventInfo)

    # 更新玩家官职信息
    def onClientGetPlayersUseOfficial(self, playerType,id):
        isOut = officialPermissionConfig.officialPermissionConfig[id]["isOutLine"]
        canRepeat = officialPermissionConfig.officialPermissionConfig[id]["canRepeat"]
        if playerType == Get_Friend:
            if len(self.friendDBIDList) <= 0:
                list = []
                self.client.onGetPlayersUseOfficial(list)
                return
            KBEngine.globalData["PlayerMgr"].getOnlineFriends(self.databaseID,self.friendDBIDList,isOut,canRepeat,self.usePlayerDbidList,id)
        # 公会在线成员
        elif playerType == Get_Guild:
            if self.guildDBID <= 0:
                list = []
                self.client.onGetPlayersUseOfficial(list)
                return

            guildDBID = self.guildDBID
            param = {
                "guildDBID": guildDBID,
                "canRepeat": canRepeat,
                "isOut": isOut,
                "dbid": self.databaseID,
                "usePlayerDbidList": self.usePlayerDbidList,
                "guildMemberDBIDList": self.guildMemberDBIDList,
                "id": id,
            }
            officialMgr = KBEngine.globalData["OfficialMgr"]
            officialMgr.onCmd("onCmdGetGuildMembers", param)

        # 陌生人
        elif playerType == Get_Others:
            self.onGetOthersList(isOut,canRepeat,self.usePlayerDbidList,id)
        # 黑名单
        else:
            if len(self.blackDBIDList) <= 0:
                list = []
                self.client.onGetPlayersUseOfficial(list)
                return
            KBEngine.globalData["PlayerMgr"].getOnlineFriends(self.databaseID, self.blackDBIDList,isOut,canRepeat,self.usePlayerDbidList,id)

    # 获取玩家信息
    def onGetPlayers(self,list):
        self.client.onGetPlayersUseOfficial(list)

    # 获取当前官职权限
    def onClientGetPermissionInfoList(self):
        self.client.onGetPermissionInfo(self.permissionInfoList)

    # 更新玩家官权
    def onUpdatePermissionInfo(self,officialID,playerMb):
        config = officialPermissionConfig.officialPermissionConfig
        for item in playerMb.permissionInfoList:
            if item["type"] == 1:
                item["useTimes"] = config[item["id"]]["haveTimes"][officialID - 1]
            else:
                nowLimit = config[item["id"]]["haveTimes"][officialID - 1]
                nowTimes = nowLimit - item["haveTimes"]
                if nowTimes <= 0:
                    nowTimes = 0
                lastTimes = item["useTimes"]
                times = lastTimes + nowTimes
                if times >= nowLimit:
                    times = nowLimit
                item["useTimes"] = times
            item["haveTimes"] = config[item["id"]]["haveTimes"][officialID - 1]
            item["officialId"] = officialID

    # 获取在线陌生人
    def onGetOthersList(self,isOut,canRepeat,usePlayerDbidList,id):
        selfLevel = self.level
        excludeList = self.friendDBIDList + self.blackFriendInfoList
        excludeList.append(self.databaseID)
        KBEngine.globalData["PlayerMgr"].getOthersList(self.databaseID, excludeList, selfLevel,isOut,canRepeat,usePlayerDbidList,id)


    # 返回陌生人Dbid
    def onSenOthersList(self,param):
        self.guildMemberDBIDList = []
        recommendList = param["recommendList"]
        canRepeat = param["canRepeat"]
        usePlayerDbidList = param["usePlayerDbidList"]
        isOut = param["isOut"]
        id = param["id"]
        KBEngine.globalData["PlayerMgr"].getOnlineFriends(self.databaseID,recommendList,isOut,canRepeat,usePlayerDbidList,id)

    # 领取俸禄
    def onClientGetOffficialReward(self,euro):
        self.euro += euro
        self.officialReward = 1
        self.client.signUpCallBack(OfficialModulerror.get_official_reward)

    # 购买行动力
    def onClientBuyLinePower(self):
        config = vipConfig.VipConfig[self.vipLevel]
        if self.buyLinePower == config["buyLinePower"]:
            self.client.signUpCallBack(OfficialModulerror.buy_linePower_fail)
            return
        config = CommonConfig.CommonConfig[23]
        if self.delMoneyByType(Diamond_type, int(config["value"])) is False:
            return
        self.linePower += 5
        self.buyLinePower += 1
        self.client.signUpCallBack(OfficialModulerror.buy_linePower_sucess)


    # 官职信息
    def onClientGetOfficialInfo(self,officialID):

        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "officialId": officialID,
        }
        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdGetOfficialRankValue", param)


    # 低级  参加考试
    def onClientTakeTest(self, dbid, officialId):
        config = officialConfig.OfficialConfig[officialId]
        if self.consulmeCost(officialId) is False:
           return
        if self.level < config["needLevel"]:
            return
        self.client.passTest(officialId)


    # 中级  开始挑战
    def onClientPVE(self, dbid, officialId):
        config = officialConfig.OfficialConfig[officialId]
        if self.consulmeCost(officialId) is False:
            return
        if self.level < config["needLevel"]:
            return

    # 高级  报名
    def onClientSignUp(self,dbid, officialId):
        param = {
            "playerMB": self,
            "officialId": officialId,
        }
        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdGetOfficialInfo", param)


    # 确定报名
    def onClientOkSignUp(self,dbid, officialId):
        day = util.getWeekDay()
        if day == 1 or day == 4:
            canSignUp = True
        else:
            canSignUp = False

        if canSignUp == True:
            now = datetime.datetime.now()
            if now.hour >= 9 and now.hour <= 18:
                canSignUp = True
            else:
                canSignUp = False

        if canSignUp == False:
            self.client.canNotSignUp()
            return

        config = officialConfig.OfficialConfig[officialId]
        if self.consulmeCost(officialId) is False:
            return
        if self.level < config["needLevel"]:
            return
        if self.guildLevel < config["guildLevel"]:
            return

        param = {
            "playerMB": self,
            "officialId": officialId,
            "dbid": dbid,
            "name": self.name,
            "level": self.level,
            "guildName": self.guildName,
        }
        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdOkSignUp", param)

    # 获取记录信息
    def onClientGetRecordEvent(self,type):
        list = []
        for item in self.officialEventList:
            if item["eventType"] == type:
                list.append(item)
        self.client.onGetRecordEvent(list)

    # 删除事件
    def onClientClearEvent(self,index):
        if index < 0:
            self.officialEventList = []
            return
        self.officialEventList.remove(self.officialEventList[index])

    # 挑战同事
    def onClientFightColleagues(self,clleaguesDbid,officialID):
        if self.linePower < 1:
            self.client.signUpCallBack(OfficialModulerror.linePower_is_not_enough)
            return
        self.linePower -= 1

        param = {
            "playerMB": self,
            "officialId": officialID,
            "databaseID": self.databaseID,
            "playerID": clleaguesDbid,
            "fightValue": self.fightValue,
            "name": self.name,
            "photoIndex": self.photoIndex,
            "usePlayerDbidList": self.usePlayerDbidList,
            "permissionInfoList": self.permissionInfoList,
            "permissionInfoID": 15,
        }
        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdFightColleagues", param)

    # 废除官员
    def onClientAbolitionOfficials(self,clleaguesDbid,officialID):
        if self.linePower < 2:
            self.client.signUpCallBack(OfficialModulerror.linePower_is_not_enough)
            return
        self.linePower -= 2

        param = {
            "playerMB": self,
            "databaseID": self.databaseID,
            "playerID": clleaguesDbid,
            "myOfficialId": self.officialPosition,
            "officialId": officialID,
            "fightValue": self.fightValue,
            "name": self.name,
            "photoIndex": self.photoIndex,
            "usePlayerDbidList": self.usePlayerDbidList,
            "permissionInfoList": self.permissionInfoList,
            "permissionInfoID": 11,
        }
        KBEngine.globalData["PlayerMgr"].getPlayerUsePrmissionInfo(param)

    # 开始挑战
    def onClientStartPromotion(self, cloneID,officialID):
        if self.inActionType == ActionTypeEnum.official_promotion:
            return

        config = cloneConfig.CloneConfig[cloneID]

        # 体力检查
        needPower = config["needBodyPower"]

        if self.bodyPower < needPower:
            self.client.onCloneError(CloneModuleError.clone_not_enough_power)

        self.inActionType = ActionTypeEnum.official_promotion
        self.cloneID = cloneID

        self.promotionID = officialID
        param = {
            "roomID": self.id,
            "avatarMB": self,
            "actionType": ActionTypeEnum.official_promotion
        }

        KBEngine.globalData["RoomMgr"].onCmd("onCreateRoom", param)

    # 战斗结束 返回结果
    def onOfficialEndResult(self, avatarAID, aScore, avatarBID, bScore):

        self.inActionType = ActionTypeEnum.action_clone

        if hasattr(self, "roomID"):
            room = KBEngine.entities.get(self.roomID)
            if room is not None:
                room.cell.destroyRoom()

        if aScore <= bScore:
            self.client.signUpCallBack(OfficialModulerror.promotion_fail)
            return
        else:
            self.onClientPromoteOfficial(self.promotionID)


    # 玩家晋升官职 低级跟中级
    def onClientPromoteOfficial(self,officialId):
        # 答题或者挑战胜利 可以任职 刷新排行榜 重置玩家信息
        self.onResertPlayerOfficial(officialId)

        self.client.promoteOfficialSucess(officialId,self.maxOffical)
        # 当上该官职 加入排行榜
        self.updateOfficialValueRank(officialId)

    # 获取积分排行
    def onClientGetIntegralRank(self,officialId):

        param = {
            "playerMB": self,
            "officialId": officialId,
        }

        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdGetIntegralRank", param)

    # 获取对阵信息
    def onClientGetMatchPlayer(self,officialId,turn):

        param = {
            "playerMB": self,
            "officialId": officialId,
            "turn": turn,
        }

        officialMgr = KBEngine.globalData["OfficialMgr"]
        officialMgr.onCmd("onCmdGetMatchPlayer", param)
    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    # 消耗品
    def consulmeCost(self,officialID):
        config = officialConfig.OfficialConfig[officialID]
        if self.delMoneyByType(Euro_type, int(config["needCost"][0])) is False:
            return False
        if self.fame < int(config["needCost"][1]):
            self.client.signUpCallBack(OfficialModulerror.fame_is_not_enough)
            return False
        else:
            self.fame = self.fame - int(config["needCost"][1])
        return True

    # 玩家晋升官职或者更新任职点
    def updateOfficialValueRank(self,officialId,avatar = None):
        config = officialConfig.OfficialConfig[officialId]
        if avatar != None:
            playerMB = avatar
        else:
            playerMB = self
        # 当前官职限制人数
        limit = config["limit"]
        if limit == 0:
            limit = 9999999

        param = {
            "playerMB": playerMB,
            "dbid": playerMB.databaseID,
            "name": playerMB.name,
            "guildName": playerMB.guildName,
            "limit": limit,
            "officialId": officialId,
        }

        officialMgr = KBEngine.globalData["OfficialMgr"]

        officialMgr.onCmd("onCmdUpdateOfficialValueRank", param)

    # 副本创建完毕
    def onAutoRoomCreateOfficialSuccCB(self, param):
        roomMB = param["roomMB"]
        self.roomID = roomMB.id
        self.roomUUID = param["roomID"]
        if self.transMySelfNpc(param, {}):
            if "isNpc" in param:
                baseProp = {
                    "avatarB": param["avatarB"],
                    "roomID": self.roomID,
                    "actionType": ActionTypeEnum.official_promotion_player
                }
                self.transNpcs(param, baseProp)


    def transMySelfNpc(self,param,roomParam):
        self.inRoom = 1
        self.inTeamcardList = []
        self.roomMB = param["roomCellMB"]
        for cardDBID in self.cardDBIDList:
            KBEngine.createBaseAnywhereFromDBID("Card", cardDBID, self.getCardInfo)


    def getCardInfo(self,baseRef, dbid, wasActive):
        if baseRef is None:
            ERROR_MSG("card is not exist")
            return

        card = KBEngine.entities.get(baseRef.id)
        playerItem = {}
        playerItem["configID_B"] = card.configID
        playerItem["shoot"] = card.shoot
        playerItem["defend"] = card.defend
        playerItem["passBall"] = card.passBall
        playerItem["trick"] = card.trick
        playerItem["reel"] = card.reel
        playerItem["steal"] = card.steal
        playerItem["controll"] = card.controll
        playerItem["tech"] = card.tech
        playerItem["pos"] = card.pos
        playerItem["keep"] = card.keep
        playerItem["health"] = card.health
        playerItem["levelSteal"] = 100
        playerItem["levelPass"] = 100
        playerItem["roomID"] = self.roomID
        playerItem["controllerID"] = self.id
        baseRef.destroyCard()
        self.inTeamcardList.append(playerItem)

        if len(self.inTeamcardList) == 11:
            # 自己持有的卡
            roomParam = {}
            roomParam["roomUUID"] = self.roomUUID
            roomParam["roomID"] = self.roomID
            roomParam["inTeamcardList"] = self.inTeamcardList
            roomParam["actionType"] = ActionTypeEnum.official_promotion_player
            npcController = KBEngine.createBaseLocally("NpcController", {})
            npcController.cellData["baseProp"] = roomParam
            npcController.createCellEntity(self.roomMB)
            self.npcControllerID = npcController.id



