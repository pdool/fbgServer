# -*- coding: utf-8 -*-
__author__ = 'chongxin'
import KBEngine
import util
from KBEDebug import *
import random

class Clone(KBEngine.Base):


    def __init__(self):
        KBEngine.Base.__init__(self)

        DEBUG_MSG("Base::Room.__init__")

        # self._pendingLogonEntities = []

        # 创建Cell Space
        self.createInNewSpace(None)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        self.Debug("Base::Room.onLoseCell")

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        self.Debug("Base::Room.onGetCell")
        KBEngine.globalData["CloneMgr"].onCloneGetCell(self.spaceKey,self)

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        pass

    def Debug(self, *arg):

        print("Base::Room", arg)

    def loginToRoom(self, avatar):
        """
        请求登陆到房间中
        """
        self.Debug("Base::Room.loginToRoom")

        avatar.createCell(self)

    def destroyClone(self):
        self.destroyCellEntity()
