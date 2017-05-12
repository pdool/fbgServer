# -*- coding: utf-8 -*-
import Avatar
import KBEngine
import skillConfig
import skillMainConfig
import sys
from CommonEnum import ActionTypeEnum
from KBEDebug import DEBUG_MSG, ERROR_MSG
from common.skill.SkillConditionModule import ConditionEnum

__author__ = 'chongxin'
"""
avatar 的子模块
"""
class RoomFightModule:
    def __init__(self):
        if self.actionType == ActionTypeEnum.action_clone:
            self.__initCloneProp()

        self.setRoomControllerID()
    # 初始化副本战斗信息
    def __initCloneProp(self):

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
        # 当前轮次使用的技能
        self.canUseSkillList = []



        # 初始化room的
    # 设置房间的自己的controllerID
    def setRoomControllerID(self):
        room = KBEngine.entities.get(self.roomID)
        room.setControllerID(self.id)

        # 一轮开始之前

    def beforeRound(self,curTime):
        for id in self.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            card.anger = card.anger + curTime//40 #40秒恢复1点
            # 重置临时数据
            card.resetRoundData()
            # 附加buffer的效果
            card.bufferEffect()

    def controllerAfterRound(self,result):
        ERROR_MSG("  afterRound  result  " + str(result))
        for cardId in self.inTeamcardIDList:
            card = KBEngine.entities.get(cardId)
            card.afterRound(result)



    def selectCanUseSkills(self):

        self.canUseSkillList = []
        if not isinstance(self, Avatar.Avatar):
            return []

        curPart = KBEngine.entities.get(self.roomID).curPart
        for id in self.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            skill = card.skill1_B
            skillCon = skillMainConfig.SkillMain[skill]

#             1、检查步骤适合
            if curPart not in skillCon["useStep"]:
                continue
#             2、检查怒气
            if card.anger <100:
                continue
#             3、检查condition
            condition = skillCon["condition"]
            if not card.checkCondition(condition,ConditionEnum.con_result_None):
                continue

            self.canUseSkillList.append(id)

        ERROR_MSG("  canUseSkillList  " + self.canUseSkillList.__str__())
        return self.canUseSkillList


