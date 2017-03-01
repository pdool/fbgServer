# -*- coding: utf-8 -*-
import TimerDefine
from KBEDebug import *
import util

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
from part.CloneModule import CloneModule


class Avatar(KBEngine.Entity,
             CloneModule):
    """
    角色实体
    """
    def __init__(self):

        KBEngine.Entity.__init__(self)

        for k, v in self.baseProp.items():
            DEBUG_MSG("Avatar   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)

        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, '__init__'):
                c.__init__(self)


    def onEnteredAoI( self, entity ):
        return
        ERROR_MSG("onEnteredAoI--------------" + str(type(entity)))


    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if TimerDefine.Time_destroy_avatar == userArg:
            self.destroySelf()

        # GameObject.onTimer(self, tid, userArg)
        # 调用子类的onTimer函数
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, 'onTimer'):
                c.onTimer(self,tid, userArg)
