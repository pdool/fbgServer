# -*- coding: utf-8 -*-
from CommonEnum import ActionTypeEnum
from KBEDebug import ERROR_MSG
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
        self._pendingLogonEntities[roomID] = args
         # 创建副本
        param = {"roomID":roomID,"actionType":actionType}
        KBEngine.createBaseAnywhere("Room",param,None)


    # 房间创建成功注册给管理器
    def onRoomGetCell(self,param):
        # 注册
        roomID = param["roomID"]
        roomMB = param["roomMB"]
        roomCellMB = param["roomCellMB"]
        actionType = param["actionType"]

        self.rooms[roomID] = roomMB
        args = self._pendingLogonEntities[roomID]

        ERROR_MSG("   onRoomGetCell args:  " + str(args))

        if actionType == ActionTypeEnum.league_player :

            param["leagueDBID"] = args["leagueDBID"]
            param["avatarA"] = args["avatarA"]
            param["avatarB"] = args["avatarB"]
            param["isJoinA"] = args["isJoinA"]
            param["isJoinB"] = args["isJoinB"]

            leagueMgr = KBEngine.globalData["LeagueMgr"]
            leagueMgr.onCmd("onCmdRoomCreateSuccCB", param)
        else:
            avatarMb = args["avatarMB"]
            avatarMb.onPlayerMgrCmd("onRoomCreateSuccCB", param)

        del self._pendingLogonEntities[roomID]


    def onRoomDestroy(self,param):
        roomID  = param["roomID"]

        del self.rooms[roomID]



