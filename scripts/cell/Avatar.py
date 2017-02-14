# -*- coding: utf-8 -*-

from KBEDebug import *
import util

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
class Avatar(KBEngine.Entity):
    """
    角色实体
    """
    def __init__(self):

        KBEngine.Entity.__init__(self)


        for k, v in self.baseProp.items():
            DEBUG_MSG("Avatar   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)


    def onEnteredAoI( self, entity ):

        ERROR_MSG("onEnteredAoI--------------" + str(type(entity)))