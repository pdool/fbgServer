# -*- coding: utf-8 -*-
import traceback

import cardLevelUpgradeConfig
import cloneChapterConfig
import  cloneConfig
import util
from CommonEnum import ActionTypeEnum, CloneChapterGiftEnum
from ErrorCode import CloneModuleError
from KBEDebug import *
from cardsConfig import cardsConfig

__author__ = 'chongxin'
__createTime__  = '2017年2月5日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):
        self.inActionType = ActionTypeEnum.action_none

        self.cloneIDToIndex = {}
        for index in range(len(self.passCloneInfo)):
            cloneID = self.passCloneInfo[index]["cloneID"]
            self.cloneIDToIndex[cloneID] = index
    # 客户端掉线
    def onClientDeath(self):

        if self.inActionType == ActionTypeEnum.action_clone or self.inActionType == ActionTypeEnum.league_clone or (
                self.inActionType == ActionTypeEnum.league_player) or (
            self.inActionType == ActionTypeEnum.action_arena) or self.inActionType == ActionTypeEnum.official_promotion:
            self.onClientLeaveClone()



    # 创建角色时默认解锁第一章节
    def onCreateRoleUnlockChapter(self):
        chapterInfo = {
            "chapterID"     : 1,
            "star"          : 0,
            "gift1"         : CloneChapterGiftEnum.not_get,
            "gift2"         : CloneChapterGiftEnum.not_get,
            "gift3"         : CloneChapterGiftEnum.not_get,
            "gift4"         : CloneChapterGiftEnum.not_get,
        }
        self.chapterInfo.append(chapterInfo)

        config = cloneConfig.CloneConfig[1001]
        cloneInfo = {
            "cloneID": 1001,
            "star": 0,
            "restCount": config["dailyChallengeCount"]
        }
        self.passCloneInfo.append(cloneInfo)
        self.cloneIDToIndex[1001] = len(self.passCloneInfo) - 1

    # ===============================客户端消息================================================================================

    # 获得所有的副本信息
    def onClientGetAllCloneInfo(self):

        ERROR_MSG("onClientGetAllCloneInfo  " + self.passCloneInfo.__str__())

        self.client.onGetAllCloneInfo(self.chapterInfo,self.passCloneInfo)

    # 请求进入副本
    def onClientReqEnterClone(self, cloneID):
        if self.inActionType == ActionTypeEnum.action_clone:
            return

        if cloneID not in cloneConfig.CloneConfig:
            # 配置错误
            self.client.onCloneError(CloneModuleError.clone_config_error)
            return

        if not self.isChapterOpen(cloneID):
            self.client.onCloneError(CloneModuleError.clone_chapter_not_open)
            return

        config = cloneConfig.CloneConfig[cloneID]

        # 开启等级
        startLevel = config["openLevel"]
        if self.level < startLevel:
            self.client.onCloneError(CloneModuleError.clone_not_open)
            return
        # 剩余次数
        if cloneID not in self.cloneIDToIndex:
            self.client.onCloneError(CloneModuleError.clone_not_open)
            return

        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]

        if cloneInfo["restCount"] <= 0:
            self.client.onCloneError(CloneModuleError.clone_not_enough_rest_count)
            return

        cloneInfo["restCount"] = cloneInfo["restCount"]  - 1
        # 体力检查
        needPower = config["needBodyPower"]

        if self.bodyPower < needPower:
            self.client.onCloneError(CloneModuleError.clone_not_enough_power)

        ERROR_MSG("-------------------player is in clone ---------------------------------------")
        self.inActionType = ActionTypeEnum.action_clone
        self.cloneID = cloneID
        param = {
            "roomID": self.id,
            "avatarMB": self,
            "actionType": ActionTypeEnum.action_clone
        }

        KBEngine.globalData["RoomMgr"].onCmd("onCreateRoom", param)



    # 客户端请求扫荡
    def onClientSweep(self, cloneID, num):
        # 检查是不是可以扫荡
        if cloneID not in self.cloneIDToIndex:
            self.client.onCloneError(CloneModuleError.clone_not_open)
            return
        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]

        star = cloneInfo["star"]

        if star < 3:
            self.client.onCloneError(CloneModuleError.clone_not_enough_3Star)
            return

        drops = {}
        exp = 0
        euro = 0
        for i in range(num):
            exp1,euro1,dropMap = self.sweepOnce(cloneID)
            exp = exp + exp1
            euro = euro + euro1
            if not self.canPutInBag(dropMap):
                break

            for  itemID ,num in dropMap.items():
                if itemID in drops:
                    drops[itemID] =  num
                else:
                    drops[itemID] =  num

        self.euro = self.euro + euro
        changeLevel = []
        for cardID in self.cardIDList:
            changeLevel,changeExp = self.onCardLevelUp(cardID,exp)

        self.client.onSweepResult(i,list(drops.keys()),list(drops.values()))


    # 离开副本
    def onClientLeaveClone(self):

        ERROR_MSG("---------------------  onClientLeaveClone -----------------------------")
        if self.inActionType == ActionTypeEnum.league_clone or self.inActionType == ActionTypeEnum.league_player:
            param = {
                "selfDBID": self.databaseID,
            }
            leagueMgr = KBEngine.globalData["LeagueMgr"]
            leagueMgr.onCmd("onCmdLeaveMatch", param)

            pass

        self.inActionType = ActionTypeEnum.action_none


        if hasattr(self,"roomID"):
            room = KBEngine.entities.get(self.roomID)
            if room is not None:
                room.cell.destroyRoom()



    # 领取章节奖励
    def onClientGetChapterReward(self,chapterID,index):

        if index < 1 or index >  4:
            self.client.onCloneError(CloneModuleError.clone_config_error)
            return

        if chapterID not in cloneChapterConfig.CloneChapterConfig:
            self.client.onCloneError(CloneModuleError.clone_config_error)
            return

        ERROR_MSG("  chapterID  " + str(chapterID) + "   index   " + str(index))

        chapterConfig = cloneChapterConfig.CloneChapterConfig[chapterID]

        needStar = chapterConfig["star"+ str(index)]
        giftConfig = chapterConfig["star" + str(index) +"Gift" ]

        key = "gift" +  str(index)

        for info in self.chapterInfo:
            if info["chapterID"] == chapterID:

                if info[key] == CloneChapterGiftEnum.get:
                    self.client.onCloneError(CloneModuleError.clone_chapter_reward_has_got)
                    return

                hasStar = info["star"]
                if hasStar >= needStar:
                    self.putDropToBag(giftConfig)
                    info[key] = CloneChapterGiftEnum.get

                    self.client.onGetChapterReward()

                    return

                self.client.onCloneError(CloneModuleError.clone_chapter_reward_not_enough_star)
                return

        self.client.onCloneError(CloneModuleError.clone_config_error)




# ====================================工具函数=======================================================================

# ====================================工具函数===========================================================================

    # 联赛玩家和机器人
    def leagueVSRobot(self):

        cloneID =  1001

        self.inActionType = ActionTypeEnum.league_clone
        self.cloneID = cloneID
        param = {
            "roomID": self.id,
            "avatarMB": self,
            "actionType": ActionTypeEnum.league_clone
        }

        KBEngine.globalData["RoomMgr"].onCmd("onCreateRoom", param)

        pass


    # 扫荡一次
    def sweepOnce(self,cloneID):
        config = cloneConfig.CloneConfig[cloneID]
        needPower = config["needBodyPower"]
        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]
        if cloneInfo["restCount"] <= 0:
            self.client.onCloneError(CloneModuleError.clone_not_enough_rest_count)
            return

        ERROR_MSG("sweepOnce   bodyPower  " + str(self.bodyPower) +"    needPower  " + str(needPower) )

        self.bodyPower = self.bodyPower - needPower
        cloneInfo["restCount"] = cloneInfo["restCount"] - 1

        exp,euro,dropMap =  self.getDropByCloneID(cloneID)

        return exp,euro,dropMap

    # 根据副本ID 获得掉落
    def getDropByCloneID(self,cloneID):
        dropConfig = cloneConfig.CloneConfig[cloneID]["drop"]
        exp = cloneConfig.CloneConfig[cloneID]["exp"]
        euro = cloneConfig.CloneConfig[cloneID]["euro"]
        dropMap = {}
        for itemID,config in dropConfig.items():
            percent = config[1]
            p = util.randFunc()
            if p <= percent:
                dropMap[itemID] = config[0]

        return exp,euro,dropMap


    # 副本创建完毕
    def onRoomCreateSuccCB(self,param):
        roomMB = param["roomMB"]
        roomCellMB = param["roomCellMB"]
        self.roomID = roomMB.id
        if self.transMySelf(param,{"cloneID" :self.cloneID} ) is True:


            actionType = param["actionType"]
            baseProp = { "roomID": roomMB.id,"actionType":actionType,"cloneID":self.cloneID}
            self.transNpcs(param,baseProp)

    def transMySelf(self,param,roomParam):
        self.inRoom = 1
        roomMB = param["roomMB"]
        roomCellMB = param["roomCellMB"]
        actionType = param["actionType"]
        roomID = param["roomID"]

        # ==============传送所有的卡牌进去==============================================================================
        ERROR_MSG("   inTeamcardIDList   " + self.inTeamcardIDList.__str__())
        for inTeamCardId in self.inTeamcardIDList:

            # 把上阵的卡牌传送进去
            card = KBEngine.entities.get(inTeamCardId)

            levelConfig = cardLevelUpgradeConfig.cardLevelUpgradeConfig[card.level]

            if card.pos == 1:
                keeperID = card.id
                ERROR_MSG("-------------avatar-------keeperID----------------------------  " + str(keeperID))

            baseProp = {"shoot"         : card.shoot,
                        "defend"        : card.defend,
                        "passBall"      : card.passBall,
                        "trick"         : card.trick,
                        "reel"          : card.reel,
                        "steal"         : card.steal,
                        "controll"      : card.controll,
                        "keep"          : card.keep,
                        "tech"          : card.tech,
                        "health"        : card.health,
                        "levelSteal"    :  levelConfig["levelStealRatio"],
                        "levelPass"     :  levelConfig["levelPassRatio"],
                        "pos"           : card.pos,
                        "configID_B"    : card.configID,
                        "skill1_B"       : card.skill1//100,
                        "skill1_Level"   : card.skill1%100,
                        "skill2_B"          : card.skill2 // 100,
                        "skill2_Level"  : card.skill2 % 100,
                        "roomID"            : roomMB.id,
                        "controllerID"      : self.id
                        }
            try:
                card.cellData["baseProp"] = baseProp
            except:
                ERROR_MSG("======cell data not exist =======  " + str(card.configID) + "   " + str(card.id))



            card.createCellEntity(roomCellMB)


        # ===============传送avatar 进去================================================================================

        roomParam["cardID"] = self.cardID
        roomParam["roomID"] = roomMB.id
        roomParam["databaseID"] = self.databaseID

        # 自己持有的卡
        roomParam["inTeamcardIDList"] = self.inTeamcardIDList
        roomParam["formation"] = self.formation
        roomParam["keeperID"] = keeperID
        roomParam["actionType"] = actionType

        self.cellData["baseProp"] = roomParam

        # 把自己传送进去
        self.createCellEntity(roomCellMB)

        return True


    def transNpcs(self,param,baseProp):

        ERROR_MSG("   transNpcs    baseProp    " + baseProp.__str__())

        roomCellMB = param["roomCellMB"]
        actionType = param["actionType"]
        npcController = KBEngine.createBaseLocally("NpcController",{})
        npcController.cellData["baseProp"] = baseProp
        npcController.createCellEntity(roomCellMB)
        self.npcControllerID = npcController.id



    # 副本结束

    def onCloneRoomEndResult(self,avatarAID,aScore,avatarBID,bScore,footBallFeast):

        ERROR_MSG("onCloneRoomEndResult  avatarAID" + str(avatarAID) + "   self.id   " + str(self.id))

        cloneID = self.cloneID
        myScore = aScore
        enemyScore = bScore
        if avatarBID == self.id:
            myScore = bScore
            enemyScore = aScore

        star = myScore - enemyScore
        config = cloneConfig.CloneConfig[cloneID]
        needPower = config["needBodyPower"]

        if star <= 0:
            # 失败
            needPower = round(needPower / 2)
            ERROR_MSG("onCloneRoomEndResult  1  bodyPower  " + str(self.bodyPower) + "    needPower  " + str(needPower))
            self.bodyPower = self.bodyPower - needPower
            self.client.onCloneFail(myScore, enemyScore)
            return

        elif star > 3:
            # 三星
            star = 3
        ERROR_MSG("onCloneRoomEndResult 2   bodyPower  " + str(self.bodyPower) + "    needPower  " + str(needPower))
        self.bodyPower = self.bodyPower - needPower
        # 其他 1,2,3 就是1,2,3

        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]
        chapterInfo = self.getChapterInfo(cloneID)

        if cloneInfo["star"] < star:
            # 更新章节的星
            chapterInfo["star"] = chapterInfo["star"] + star - cloneInfo["star"]
            cloneInfo["star"] = star
        chapterStar = chapterInfo["star"]

        exp,euro,dropMap = self.getDropByCloneID(cloneID)
        if footBallFeast == 1:
            exp *= 2
        self.euro = self.euro + euro

        ERROR_MSG("      onCloneRoomEndResult        " + self.cardIDList.__str__())

        try:
            changeLevels = []
            for i in range(len(self.cardIDList)):
                cardID = self.cardIDList[i]
                changeLevel, changeExp = self.onCardLevelUp(cardID, exp)
        except:
            traceback.print_exc()


        if not self.putDropToBag(dropMap):
            # 背包溢出
            return

        ERROR_MSG("myscore   " + str(myScore) +"      enemyScore    "+ str(enemyScore) +"  star  " + str(star) +"  dropMap " + dropMap.__str__())
        self.client.onCloneSucc(myScore, enemyScore, star, chapterStar, list(dropMap.keys()))

        # 解锁新章节
        self.openNextClone(cloneID)




    # 副本所在章节是否开启
    def isChapterOpen(self,cloneID):
        config = cloneConfig.CloneConfig[cloneID]
        # 章节是否开启
        chapterID = config["chapterID"]
        for x in self.chapterInfo:
            if x["chapterID"] == chapterID:
                return True

        return False

    # 获得副本所在章节信息
    def getChapterInfo(self,cloneID):
        config = cloneConfig.CloneConfig[cloneID]
        # 章节是否开启
        chapterID = config["chapterID"]
        for x in self.chapterInfo:
            if x["chapterID"] == chapterID:
                return x

        return None
    # 放进背包
    def putDropToBag(self,dropMap):

        for k,v in dropMap.items():

            if not self.putItemInBag(k,v):
                return False

        return True

    # 解锁新章节
    def unlockNewChapter(self,chapterID):

        for x in self.chapterInfo:
            if x["chapterID"] == chapterID:
                return
        chapterInfo = {
            "chapterID": chapterID,
            "star": 0,
            "gift1": CloneChapterGiftEnum.not_get,
            "gift2": CloneChapterGiftEnum.not_get,
            "gift3": CloneChapterGiftEnum.not_get,
            "gift4": CloneChapterGiftEnum.not_get,
        }
        self.chapterInfo.append(chapterInfo)

    def openNextClone(self,cloneID):
        # 1、判断是否是解锁副本
        for chapterID in range(2,len(cloneChapterConfig.CloneChapterConfig)):
            config = cloneChapterConfig.CloneChapterConfig[chapterID]
            openCloneID = config["openCloneID"]

            if openCloneID == cloneID:
                for x in self.chapterInfo:
                    if x["chapterID"] == chapterID:
                        return
                        # 解锁新章节
                    self.unlockNewChapter(chapterID)

                    firstCloneID = config["firstCloneID"]
                    # 已经存在了
                    if firstCloneID in self.cloneIDToIndex:
                        return

                    config = cloneConfig.CloneConfig[firstCloneID]
                    cloneInfo = {
                        "cloneID": firstCloneID,
                        "star": 0,
                        "restCount": config["dailyChallengeCount"]
                    }
                    self.passCloneInfo.append(cloneInfo)
                    self.cloneIDToIndex[firstCloneID] = len(self.passCloneInfo) - 1

                    return

        if cloneID + 1 in self.cloneIDToIndex:
            return

        config = cloneConfig.CloneConfig[cloneID + 1]
        cloneInfo = {
            "cloneID": cloneID + 1,
            "star": 0,
            "restCount": config["dailyChallengeCount"]
        }
        self.passCloneInfo.append(cloneInfo)
        self.cloneIDToIndex[cloneID + 1] = len(self.passCloneInfo) - 1







    def onGmOpenClone(self,cloneID):
        ERROR_MSG("  onGmOpenClone   " + str(cloneID))
        start = cloneID - cloneID%1000 + 1
        chapterID = cloneID//1000

        self.unlockNewChapter(chapterID)

        x = start
        for x in range(start,cloneID + 1):
            if x in self.cloneIDToIndex:
                continue

            config = cloneConfig.CloneConfig[x]
            cloneInfo = {
                "cloneID": x,
                "star": 3,
                "restCount": config["dailyChallengeCount"]
            }
            self.passCloneInfo.append(cloneInfo)
            self.cloneIDToIndex[x] = len(self.passCloneInfo) - 1
















