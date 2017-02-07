# -*- coding: utf-8 -*-
import KBEngine
import cloneConfig
import monsterConfig
from KBEDebug import *

class Clone(KBEngine.Entity):

#========================KBE方法=================================================
    """
    游戏房间
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        print("Cell::clone.__init__")
        KBEngine.globalData["room_%i" % self.spaceID] = self.base

        self.initMonster()

    def initMonster(self):

        cloneNpcConfig = cloneConfig.CloneConfig[self.cloneID]

        npcTuple = cloneNpcConfig["npcTuple"]

        formationTuple = cloneNpcConfig["formationTuple"]

        ERROR_MSG("--------spaceID-------------------" + str(self.spaceID))
        for i in range(11):
            npcID = npcTuple[i]
            if npcID not in monsterConfig.MonsterConfig:
                DEBUG_MSG("wrong config")
                continue
            baseProp = monsterConfig.MonsterConfig[npcID].copy()
            baseProp["pos"] = formationTuple[i]
            param = {"baseProp":baseProp}

            position = (0.0,0.0,0.0)
            direction = (0.0,0.0,0.0)
            KBEngine.createEntity("Monster",self.spaceID,position,direction,param)

































    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        DEBUG_MSG(tid, userArg)

    def onDestroy(self):
        """
        KBEngine method.
        """
        del KBEngine.globalData["room_%i" % self.spaceID]
        self.destroySpace()

#========================房间内事件=================================================

    def onEnter(self, entityMailbox):
        """
        进入场景
        """
        print("Cell::Room.onEnter")

    def onLeave(self, entityID):
        """
        离开场景
        """
        print("Cell::Room.onLeave")