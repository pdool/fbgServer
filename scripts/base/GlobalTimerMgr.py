# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'

class GlobalTimerMgr(KBEngine.Base):
    def __init__(self):
        KBEngine.Base.__init__(self)
        KBEngine.globalData["GlobalTimerMgr"] = self
        self.initTimer()
        pass

    def onTimer(self, tid, userArg):
        ERROR_MSG("ontimer" + str(userArg))
        pass

    """
    全服的Timer在这里添加
    """
    def initTimer(self):
        ERROR_MSG("GlobalTimerMgr  init       ")
        pass