# -*- coding: utf-8 -*-
import util
from CommonEnum import ActionTypeEnum
from ErrorCode import CloneModuleError
from KBEDebug import *
import  cloneConfig
import cardLevelUpgradeConfig

__author__ = 'chongxin'
__createTime__  = '2017年2月5日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):
        self.inClone = False

        self.cloneIDToIndex = {}
        for index in range(len(self.passCloneInfo)):
            cloneID = self.passCloneInfo[index]
            self.cloneIDToIndex[cloneID] = index
    # 客户端掉线
    def onClientDeath(self):

        self.onClientLeaveClone()
        pass


    def onClientGetAllCloneInfo(self):
        self.client.onGetAllCloneInfo(self.passCloneInfo)

    def onCellReturnScore(self,argMap):

        cloneID = argMap["cloneID"]
        myScore = argMap["myScore"]
        enemyScore = argMap["enemyScore"]



    # 客户端请求扫荡
    def onClientSweep(self,cloneID,num):
        # 检查是不是可以扫荡
        if cloneID not in self.cloneIDToIndex:
            self.client.onCloneError(CloneModuleError.clone_not_open)
            return
        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]

        star = cloneInfo["star"]

        if star < 3 :
            self.client.onCloneError(CloneModuleError.clone_not_enough_3Star)
            return

        self.sweepOnce(cloneID)
    # 扫荡一次
    def sweepOnce(self,cloneID):
        config = cloneConfig.CloneConfig[cloneID]
        needPower = config["needBodyPower"]
        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]
        if cloneInfo["restCount"] <= 0:
            self.client.onCloneError(CloneModuleError.clone_not_enough_rest_count)
            return

        self.getDropByCloneID(cloneID)
    # 根据副本ID 获得掉落
    def getDropByCloneID(self,cloneID):
        pass


    # 请求进入副本
    def onClientReqEnterClone(self,cloneID):
        if self.inClone == True:
            return
        self.inClone = ActionTypeEnum.action_clone
        self.cloneID = cloneID
        config = cloneConfig.CloneConfig[cloneID]
        # 开启等级
        startLevel = config["openLevel"]
        if self.level < startLevel:
            self.client.onCloneError(CloneModuleError.clone_not_open)
            return
        # 剩余次数
        if cloneID not in self.cloneIDToIndex:

            cloneInfo = {
                "cloneID"   : cloneID,
                "star"       : 0,
                "restCount" :config["dailyChallengeCount"]
            }
            self.passCloneInfo.append(cloneInfo)
            self.cloneIDToIndex[cloneID] = len(self.passCloneInfo) -1

        cloneInfo = self.passCloneInfo[self.cloneIDToIndex[cloneID]]

        if cloneInfo["restCount"] <= 0:
            self.client.onCloneError(CloneModuleError.clone_not_enough_rest_count)
            return
        # 体力检查
        needPower = config["needBodyPower"]

        if self.bodyPower < needPower:
            self.client.onCloneError(CloneModuleError.clone_not_enough_power)


        ERROR_MSG("--------------------------player is in clone ------------------------------------------------------------")
        roomMgr = KBEngine.globalData["RoomMgr"]
        param= {
            "roomID"        : self.id,
            "avatarMB"      : self,
            "actionType"    : ActionTypeEnum.action_clone
        }

        roomMgr.onCmd("onCreateRoom",param)


    def onClientLeaveClone(self):

        ERROR_MSG("---------------------  onClientLeaveClone -----------------------------")

        self.inClone = False
        if self.cell is not None:
            self.destroyCellEntity()

        for id in self.cardIDList:
            card = KBEngine.entities.get(id)
            if card.cell is None:
                continue
            card.destroyCardCell()

        room = KBEngine.entities.get(self.roomID)
        if room is not None:
            room.onCmd("destroyRoom",{})

        if self.npcController is not None:
            self.npcController.onCmd("destroyNpcController", {})



    # 副本创建完毕
    def onRoomCreateSuccCB(self,param):
        roomMB = param["roomMB"]
        self.roomID = roomMB.id
        self.transMySelf(param)
        self.transNpcs(param)

    def transMySelf(self,param):
        roomMB = param["roomMB"]
        actionType = param["actionType"]
        roomID = param["roomID"]

        # ==============传送所有的卡牌进去==============================================================================
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
                        "skill1_B"       : card.skill1,
                        "skill2_B"       : card.skill2,
                        "roomID"       : roomMB.id,
                        "controllerID"  : self.id
                        }

            try:
                card.cellData["baseProp"] = baseProp
            except:
                ERROR_MSG("======cell data not exist =======  " + str(card.configID) + "   " + str(card.id))



            card.createCellEntity(roomMB.cell)


        # ===============传送avatar 进去================================================================================

        baseProp = {"cardID": self.cardID, "roomID": roomMB.id,"cloneID":self.cloneID}
        # 自己持有的卡
        baseProp["inTeamcardIDList"] = self.inTeamcardIDList
        baseProp["formation"] = self.formation
        baseProp["keeperID"] = keeperID
        baseProp["actionType"] = actionType

        self.cellData["baseProp"] = baseProp

        # 把自己传送进去
        self.createCellEntity(roomMB.cell)


    def transNpcs(self,param):
        roomMB = param["roomMB"]
        actionType = param["actionType"]
        roomID = param["roomID"]

        npcController = KBEngine.createBaseLocally("NpcController",{})
        baseProp = { "roomID": roomMB.id,"actionType":actionType,"cloneID":self.cloneID}
        npcController.cellData["baseProp"] = baseProp
        npcController.createCellEntity(roomMB.cell)
        self.npcController = npcController





























