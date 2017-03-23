# -*- coding: utf-8 -*-

from KBEDebug import *


__author__ = 'chongxin'
__createTime__  = '2017年2月15日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):

        print(" avatar clone init -------------------------")
        self.__initProp()

        self.client.onReady()


    def __initProp(self):

        self.totalAttackValue = 0.0
        self.totalDefendValue = 0.0
        self.totalControllValue = 0.0
        # 上一轮的攻击者
        self.preAttackId = -1
        # 上一轮的防守者 列表
        self.preDefIds = []
        # 上一轮是否完美助攻的射门系数
        self.o1 = 1

        self.atkList = []
        self.atkPosList =[]
        self.defList = []

        # 技术统计
        # 被抢断
        self.beTrick = 0
        # 射门成功
        self.shootSucc = 0

    # 客户端通知开始战斗

    def onClientBeginFight(self,exposedID):
        if exposedID != self.id:
            return
        cloneID = self.cloneID

        clone = KBEngine.entities.get(cloneID)

        clone.avatarID = self.id

        print(" avatar  onClientBeginFight -------------------------")
        clone.onCmdBeginFight()




    def onClientPlayAnimFinish(self,exposedID):
        if exposedID != self.id:
            return
        cloneID = self.cloneID

        clone = KBEngine.entities.get(cloneID)
        clone.onCmdPlayAnimFinish()


    def onClientSelectOp(self,exposedID,leftSkillIdList,rightSkillIdList):
        if exposedID != self.id:
            return

        cloneID = self.cloneID

        clone = KBEngine.entities.get(cloneID)

        # ERROR_MSG("-----------onClientSelectOp----------------------------  " + str(skillId))

        clone.onCmdSelectSkill(leftSkillIdList,rightSkillIdList)















