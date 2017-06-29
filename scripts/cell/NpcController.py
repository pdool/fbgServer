# -*- coding: utf-8 -*-
import TimerDefine
import cardLevelUpgradeConfig
import cloneConfig
import monsterConfig
import util
from BossDaily import BossDaily
from CommonEnum import PlayerOp, ActionTypeEnum
from KBEDebug import *

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
from common.RoomFightModule import RoomFightModule
from npcBossConfig import npcBossConfig


class NpcController(KBEngine.Entity,RoomFightModule):
    typeStr = "NpcController"
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
        if self.actionType == ActionTypeEnum.action_clone or self.actionType == ActionTypeEnum.league_clone:
            self.initMonster()
        elif self.actionType == ActionTypeEnum.action_world_boss:
            self.initWorldBossNpc()
        elif self.actionType == ActionTypeEnum.official_promotion or self.actionType == ActionTypeEnum.action_arena:
            self.initMonster()
        elif self.actionType == ActionTypeEnum.official_promotion_player or self.actionType == ActionTypeEnum.league_player:
            self.initMySlef()


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
                     "controllerID": self.id,
                     "skill2_B":2020,
                     "skill2_Level":1
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

    def initMySlef(self):
        room = KBEngine.entities.get(self.roomID)

        spaceID = room.spaceID

        ERROR_MSG("initMySlef  inTeamcardList" + str(len(self.inTeamcardList)))

        for card in self.inTeamcardList:

            position = (0.0, 0.0, 0.0)
            direction = (0.0, 0.0, 0.0)
            e = KBEngine.createEntity("Card", spaceID, position, direction, {})
            e.configID_B = card["configID_B"]
            e.shoot = card["shoot"]
            e.defend = card["defend"]
            e.passBall = card["passBall"]
            e.trick = card["trick"]
            e.reel = card["reel"]
            e.steal = card["steal"]
            e.controll = card["controll"]
            e.keep = card["keep"]
            e.tech = card["tech"]
            e.health = card["health"]
            e.pos = card["pos"]
            e.levelSteal = card["levelSteal"]
            e.levelPass = card["levelPass"]
            e.roomID = self.roomID
            e.controllerID = self.id
            errorMsg = "========monster pos ========="
            # 门将
            errorMsg = errorMsg + "      " + str(e.pos)
            if e.pos == 1:
                self.keeperID = e.id
                # ERROR_MSG("-------------------monster-----------keeperID------------------------------  " + str(e.id))
            self.inTeamcardIDList.append(e.id)
        # 告诉房间准备好了。如果都准备好了就可以开始了
        room.setReadyState(self.id,self.actionType,self.roomUUID)

    def initWorldBossNpc(self):
        room = KBEngine.entities.get(self.roomID)

        spaceID = room.spaceID

        cloneNpcConfig = npcBossConfig[self.avatarB]

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

        pass

    def onAutoSelectSkill(self):
        self.onAISelect()
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
            room.onCmdPlayAnimFinish(self.id)

    def onFirstSelect(self,room):
        room.setSelectState(self.id,PlayerOp.passball)
        room.onCmdPlayAnimFinish(self.id)
    # 副本AI(副本选择射门还是传球)
    def onSecondSelect(self,room):
        # 计算射门值
        p = room.getShootValue()

        # ERROR_MSG("              =========  onCloneSelectOp         ====================  p     "  + str(p))
        if p >= 0.4:
            # 射门
            room.setSelectState(self.id, PlayerOp.shoot)
            room.onCmdPlayAnimFinish(self.id)
        else:
            # 传球
            room.setSelectState(self.id, PlayerOp.passball)
            room.onCmdPlayAnimFinish(self.id)

    def onThirdSelect(self,room):
        room.setSelectState(self.id, PlayerOp.shoot)
        room.onCmdPlayAnimFinish(self.id)








