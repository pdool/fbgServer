# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *

import shopConfig

__author__ = 'chongxin'
__createTime__  = '2017年2月5日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):
        pass

    # 请求进入副本
    def onClientReqEnterClone(self,cloneID):
        cloneMgr = KBEngine.globalData["CloneMgr"]

        cloneMgr.reqEnterClone(self,cloneID)

    # 副本创建成功回调
    def OnCloneCreateSuccCB(self,argDict):
        spaceMB = argDict["spaceMb"]

        # spaceMB.cell.initMonster()

        baseProp = {"cardID": self.cardID}
        baseProp["cardDBIDList"] = self.inTeamcardIDList

        self.cellData["baseProp"] = baseProp

        # 把自己传送进去
        self.createCellEntity(spaceMB.cell)

        for inTeamCardId in self.inTeamcardIDList:
            # 把上阵的卡牌传送进去
            card = KBEngine.entities.get(inTeamCardId)

            baseProp = {"shoot": card.shoot, "defend": card.defend}

            card.cellData["baseProp"] = baseProp

            card.createCellEntity(spaceMB.cell)































