# -*- coding: utf-8 -*-
import KBEngine
import Math
from KBEDebug import *

class Monster(KBEngine.Entity):

#========================KBE方法=================================================
    """
    卡牌
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        # print("Cell::Monster.__init__")

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
