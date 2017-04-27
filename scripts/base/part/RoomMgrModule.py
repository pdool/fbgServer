# -*- coding: utf-8 -*-
import KBEngine
from CommonEnum import ActionType

__author__ = 'chongxin'

class RoomMgrModule:
    def __init__(self):
        pass

    def reqCreateRoom(self,actionType):
        roomID = KBEngine.genUUID64()

        self.roomID = roomID

        roomMgr = KBEngine.globalData["RoomMgr"]

        param = {
            "roomID"    : roomID,
            "avatarMB"  : self,
            "actionType" : actionType
        }

        roomMgr.onCreateRoom(param)


    def OnRoomCreateSuccCB(self,paramDict):
        roomMB = paramDict["roomMB"]
        actionType = paramDict["actionType"]
        roomID = paramDict["roomID"]

        if actionType == ActionType.action_clone:
            # 进入副本
            self.enterClone(paramDict)




