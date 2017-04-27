# -*- coding: utf-8 -*-

from KBEDebug import *

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
from interfaces.BaseModule import BaseModule


class NpcController(BaseModule):

    """
    Npc控制器
    """
    def __init__(self):
        BaseModule.__init__(self)
    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        ERROR_MSG("--------------NpcController onLoseCell-------------------------")
        self.destroy()

    def destroyNpcController( self, param ):
        ERROR_MSG("  NpcController     destroyNpcController          ")
        pass

