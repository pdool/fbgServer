# -*- coding: utf-8 -*-
from interfaces.BaseModule import BaseModule

__author__ = 'chongxin'
from KBEDebug import *


class Room(BaseModule):


    def __init__(self):
        BaseModule.__init__(self)

        DEBUG_MSG("Base::Room.__init__")
        # 创建Cell Space
        self.createInNewSpace(None)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """

        param = {
            "roomID"   : self.roomID,
        }
        KBEngine.globalData["RoomMgr"].onCmd("onRoomDestroy",param)


        ERROR_MSG("--------------Base::Room.onLoseCell-------------------------")
        self.destroy()

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        self.Debug("Base::Room.onGetCell")

        param = {
            "roomID"   : self.roomID,
            "roomMB"   : self,
            "roomCellMB"    : self.cell,
            "actionType" : self.actionType
        }

        KBEngine.globalData["RoomMgr"].onCmd("onRoomGetCell",param)

    def onTimer(self, id, userArg):
        # ERROR_MSG("ontimer" + str(userArg))
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        pass

    def Debug(self, *arg):

        print("Base::Room", arg)


    def onLoginRoom(self,param):
        pass

    def destroyRoom(self,param):
        ERROR_MSG("--------------destroyRoom-------------------------")
        if self.isDestroyed is not True and self is not None and self.cell is not None:
            self.destroyCellEntity()

    def onDestroy( self ):

        # j记得取消注册
        pass

