# -*- coding: utf-8 -*-
import TimerDefine
import cardLevelUpgradeConfig
import formationConfig
import util
from KBEDebug import *

__author__ = 'chongxin'
__createTime__  = '2017年2月5日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):
        self.inClone = False
        pass

    # 请求进入副本
    def onClientReqEnterClone(self,cloneID):
        if self.inClone == True:
            return
        self.inClone = True

        ERROR_MSG("--------------------------player is in clone ------------------------------------------------------------")
        cloneMgr = KBEngine.globalData["CloneMgr"]

        cloneMgr.reqEnterClone(self,cloneID)

    # 副本创建成功回调
    def OnCloneCreateSuccCB(self,argDict):
        spaceMB = argDict["spaceMb"]

        i = 0

        posList = formationConfig.FormationConfig[44201]["teamTuple"]

        keeperID = -1


        errorMsg = "========cards pos ========="
        for inTeamCardId in self.inTeamcardIDList:
            # 把上阵的卡牌传送进去
            card = KBEngine.entities.get(inTeamCardId)

            levelConfig = cardLevelUpgradeConfig.cardLevelUpgradeConfig[card.level]

            errorMsg = errorMsg + "    " + str(posList[i])

            if posList[i] == 1:
                keeperID = card.id
                ERROR_MSG("-------------avatar-------keeperID----------------------------  " + str(keeperID))

            baseProp = {"shoot"     : card.shoot,
                        "defend"    : card.defend,
                        "passBall"  : card.passBall,
                        "trick"      : card.trick,
                        "reel"       : card.reel,
                        "steal"      : card.steal,
                        "controll"   : card.controll,
                        "keep"        : card.keep,
                        "tech"        : card.tech,
                        "health"      : card.health,
                        "levelSteal"  :  levelConfig["levelStealRatio"],
                        "levelPass"   :  levelConfig["levelPassRatio"],
                        "pos"          : posList[i],
                        "configID_B"  : card.configID,
                        }
            i = i+ 1

            try:
                card.cellData["baseProp"] = baseProp
            except:
                ERROR_MSG("======cell data not exist =======  " + str(card.configID) + "   " + str(card.id))



            card.createCellEntity(spaceMB.cell)

        ERROR_MSG(errorMsg)
        baseProp = {"cardID": self.cardID,"cloneID":spaceMB.id}
        # 自己持有的卡
        baseProp["inTeamcardIDList"] = self.inTeamcardIDList
        baseProp["formation"] =  44201
        baseProp["keeperID"] = keeperID

        self.cellData["baseProp"] = baseProp

        # 把自己传送进去
        self.createCellEntity(spaceMB.cell)

        self.spaceMb = spaceMB


    def onClientLeaveClone(self):
        self.inClone = False

        ERROR_MSG("---------------------  onClientLeaveClone -----------------------------")

        if self.cell is not None:
            self.destroyCellEntity()

        for id in self.cardIDList:
            card = KBEngine.entities.get(id)
            if card.cell is None:
                continue
            card.destroyCardCell()

        if self.spaceMb is not None:
            self.spaceMb.destroyClone()





























