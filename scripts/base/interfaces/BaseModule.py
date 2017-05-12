# -*- coding: utf-8 -*-
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'
import KBEngine
class BaseModule(KBEngine.Base):
    def __init__(self):
        KBEngine.Base.__init__(self)

    def onCmd(self, methodName, argMap):
        if hasattr(self, methodName) is False:
            ERROR_MSG(str(self.__class__) + "  not exist method  " + methodName)
            return

        func = getattr(self, methodName)
        func(argMap)