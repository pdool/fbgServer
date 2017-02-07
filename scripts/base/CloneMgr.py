# -*- coding: utf-8 -*-
__author__ = 'chongxin'

__createTime__  = '2017年2月5日'

import KBEngine

class CloneMgr(KBEngine.Base):
    def __init__(self):
        KBEngine.Base.__init__(self)

        KBEngine.globalData["CloneMgr"] = self

        self._pendingLogonEntities = {}

        self.clones = {}


    def reqEnterClone(self,avatarMb,cloneID):

        # 加到等待创建队列
        self._pendingLogonEntities[avatarMb.id] = avatarMb
         # 创建副本
        param = {"cloneID":cloneID,"spaceKey":avatarMb.id}
        KBEngine.createBaseAnywhere("Clone",param,None)


    # 副本创建成功注册给管理器
    def onCloneGetCell(self,spaceKey,spaceMailbox):
        # 注册
        self.clones[spaceKey] = spaceMailbox

        avatarMb = self._pendingLogonEntities[spaceKey]
        argDict = {"spaceMb":spaceMailbox}
        avatarMb.onPlayerMgrCmd("OnCloneCreateSuccCB", argDict)
