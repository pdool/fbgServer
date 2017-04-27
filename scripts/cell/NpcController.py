# -*- coding: utf-8 -*-
import TimerDefine
import cloneConfig
import monsterConfig
from CommonEnum import PlayerOp
from KBEDebug import *

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
from common.RoomFightModule import RoomFightModule
from part.CloneModule import CloneModule


class NpcController(KBEngine.Entity,RoomFightModule):

    """
    Npc控制器
    """
    def __init__(self):
        for k, v in self.baseProp.items():
            DEBUG_MSG("NpcController   k  " + str(k) + "       v  " + str(v))
            self.__setattr__(k, v)

        KBEngine.Entity.__init__(self)
        RoomFightModule.__init__(self)

        self.inTeamcardIDList = []
        self.initMonster()



    def onEnteredAoI( self, entity ):
        return
        ERROR_MSG("onEnteredAoI--------------" + str(type(entity)))


    def initMonster(self):
        room = KBEngine.entities.get(self.roomID)

        spaceID = room.spaceID

        cloneNpcConfig = cloneConfig.CloneConfig[self.cloneID]

        npcTuple = cloneNpcConfig["npcTuple"]

        formationTuple = cloneNpcConfig["formationTuple"]

        errorMsg = "========monster pos ========="

        for i in range(11):
            npcID = npcTuple[i]
            if npcID not in monsterConfig.MonsterConfig:
                ERROR_MSG("wrong config")
                continue
            baseProp = monsterConfig.MonsterConfig[npcID]

            param = {"configID_B": npcID,
                     "shoot": baseProp["shoot"],
                     "defend": baseProp["defend"],
                     "passBall": baseProp["pass"],
                     "trick": baseProp["trick"],
                     "reel": baseProp["reel"],
                     "steal": baseProp["steal"],
                     "controll": baseProp["controll"],
                     "keep": baseProp["keep"],
                     "tech": baseProp["tech"],
                     "health": baseProp["health"],
                     "pos": formationTuple[i],
                     "levelSteal": baseProp["levelStealRatio"],
                     "levelPass": baseProp["levelPassRatio"],
                     "roomID": self.roomID,
                     "controllerID": self.id
                     }

            position = (0.0, 0.0, 0.0)
            direction = (0.0, 0.0, 0.0)
            e = KBEngine.createEntity("Monster", spaceID, position, direction, param)
            # 门将
            errorMsg = errorMsg + "      " + str(e.pos)
            if e.pos == 1:
                self.keeperID = e.id
                # ERROR_MSG("-------------------monster-----------keeperID------------------------------  " + str(e.id))
            self.inTeamcardIDList.append(e.id)

        ERROR_MSG(errorMsg)
        # 告诉房间准备好了。如果都准备好了就可以开始了
        room.setReadyState(self.id)


    def onAISelect(self):
        room = KBEngine.entities.get(self.roomID)

        if room.controllerID == self.id:
            curPart = room.curPart
            if curPart == 1:
                self.onFirstSelect(room)
            elif curPart == 2:
                self.onSecondSelect(room)
            elif curPart == 3:
                self.onThirdSelect(room)
        else:
            room.setSelectState(self.id, PlayerOp.defendOp)

    def onFirstSelect(self,room):
        room.setSelectState(self.id,PlayerOp.passball)
    # 副本AI(副本选择射门还是传球)
    def onSecondSelect(self,room):
        # 计算射门值
        p = room.getShootValue()

        # ERROR_MSG("              =========  onCloneSelectOp         ====================  p     "  + str(p))
        if p >= 0.4:
            # 射门
            room.setSelectState(self.id, PlayerOp.shoot)
        else:
            # 传球
            room.setSelectState(self.id, PlayerOp.passball)

    def onThirdSelect(self,room):
        room.setSelectState(self.id, PlayerOp.shoot)



