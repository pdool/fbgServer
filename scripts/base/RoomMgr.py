# -*- coding: utf-8 -*-
from interfaces.BaseModule import BaseModule

__author__ = 'chongxin'

__createTime__  = '2017年4月20日'

import KBEngine

class RoomMgr(BaseModule):
    def __init__(self):
        BaseModule.__init__(self)

        KBEngine.globalData["RoomMgr"] = self

        self._pendingLogonEntities = {}

        self.rooms = {}


    def onCreateRoom(self,args):


        roomID = args["roomID"]
        avatarMB = args["avatarMB"]
        actionType = args["actionType"]

        # 加到等待创建队列
        self._pendingLogonEntities[roomID] = avatarMB
         # 创建副本
        param = {"roomID":roomID,"actionType":actionType}
        KBEngine.createBaseAnywhere("Room",param,None)


    # 房间创建成功注册给管理器
    def onRoomGetCell(self,param):
        # 注册
        roomID = param["roomID"]
        roomMB = param["roomMB"]
        actionType = param["actionType"]

        self.rooms[roomID] = roomMB

        avatarMb = self._pendingLogonEntities[roomID]
        avatarMb.onPlayerMgrCmd("onRoomCreateSuccCB", param)



