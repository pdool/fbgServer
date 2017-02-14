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
        print("Cell::Card.__init__")

        # DEBUG_MSG(str(type(self.baseProp)))
        for k, v in self.baseProp.items():
            DEBUG_MSG("card   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)

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