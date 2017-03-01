# -*- coding: utf-8 -*-
import KBEngine
import Math
from KBEDebug import *

class Card(KBEngine.Entity):

#========================KBE方法=================================================
    """
    卡牌
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        # print("Cell::Card.__init__")

        # DEBUG_MSG(str(type(self.baseProp)))
        for k, v in self.baseProp.items():
            # DEBUG_MSG("card   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)

        self.totalAttackValue = 0.0
        self.totalDefendValue = 0.0
        self.totalControllValue = 0.0
        # 当前怪的id list
        self.inTeamcardIDList = []
        # 上一轮的攻击者
        self.preAttackId = -1
        # 当前进攻者ID
        self.curAttackID = -1
        # 上一轮的防守者 列表
        self.preDefIds = -1
        # 怪的攻击序列
        self.monsterAttackList = []
        # 当前防守者list
        self.curDefIdList = []
        # 上一轮是否完美助攻的射门系数
        self.o1 = 1

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
        pass


    def onSetBaseProp(self,baseProp):

        for k, v in self.baseProp.items():
            # DEBUG_MSG("card   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)


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