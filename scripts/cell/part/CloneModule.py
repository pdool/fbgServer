# -*- coding: utf-8 -*-
import skillConfig
from CommonEnum import PlayerOp
from ErrorCode import SkillModuleError
from KBEDebug import *
from common.RoomFightModule import RoomFightModule
from common.skill.SkillConditionModule import ConditionEnum

__author__ = 'chongxin'
__createTime__  = '2017年2月15日'
"""
副本模块
"""

class CloneModule(RoomFightModule):

    def __init__(self):

        print(" avatar clone init -------------------------")
        RoomFightModule.__init__(self)
        self.client.onReady()



    # 客户端通知开始战斗

    def onClientBeginFight(self,exposedID):
        if exposedID != self.id:
            return
        roomID = self.roomID

        room = KBEngine.entities.get(roomID)

        print(" avatar  onClientBeginFight -------------------------")
        room.setReadyState(self.id)




    def onClientPlayAnimFinish(self,exposedID):
        if exposedID != self.id:
            return
        cloneID = self.roomID

        room = KBEngine.entities.get(cloneID)
        room.onCmdPlayAnimFinish()
        ERROR_MSG("-----------onClientPlayAnimFinish-----------------cardId-----------  ")

    def onClientSelectOp(self,exposedID,op ,leftSkillIdList,rightSkillIdList):
        if exposedID != self.id:
            return

        for cardId in leftSkillIdList:
            ERROR_MSG("-----------onClientSelectOp-----------------cardId-----------  " + str(cardId))

        cloneID = self.roomID
        room = KBEngine.entities.get(cloneID)
        if op != PlayerOp.defendOp:
            # 1、检查基础操作actionType是不是对的
            if room.curPart == 1 and op != PlayerOp.passball:
                self.client.onSkillError(SkillModuleError.worong_op)
                return
            if room.curPart == 2:
                if op != PlayerOp.passball and op != PlayerOp.shoot:
                    self.client.onSkillError(SkillModuleError.worong_op)
                    return

            if room.curPart == 3 and op != PlayerOp.shoot:
                self.client.onSkillError(SkillModuleError.worong_op)
                return


        # # 自己是攻击者
        # if self.id == clone.controllerID:

        # # 2、判断是否行为是否互斥
        # skillSet = set()
        # for cardId in leftSkillIdList:
        #     card = KBEngine.entities.get(cardId)
        #     skillID = card.skill1_B
        #     skillSet.add(skillID)
        #     config = skillConfig.SkillConfig[skillID]
        #     actionType = config["actionType"]
        #     if actionType != ActionTypeEnum.any :
        #         if op != actionType:
        #             self.client.onSkillError(SkillModuleError.not_match_skill)
        #         return
        # # 3、判断技能是否互斥
        # for cardId in leftSkillIdList:
        #     card = KBEngine.entities.get(cardId)
        #     skillID = card.skill1_B
        #     config = skillConfig.SkillConfig[skillID]
        #     rejectSkillSet = set(config["rejectSkillID"])
        #
        #     if len(rejectSkillSet.intersection(skillSet)) >0:
        #         self.client.onSkillError(SkillModuleError.not_match_skill)
        #         return

        self.skillList = leftSkillIdList

        result = ConditionEnum.con_result_None
        succSkillList = []
        for cardId in leftSkillIdList:
            card = KBEngine.entities.get(cardId)
            skillID = card.skill1_B
            if card.useSkill(skillID,result) is True:
                succSkillList.append(card.skill1_B)

        room.setSelectState(self.id,op)

        ERROR_MSG("       op     result    is " + str(result))


        #
        # succ = "succSkillList ==========="
        # for ski in succSkillList:
        #     succ = succ + str(ski)
        # ERROR_MSG(succ)
        #
        # self.client.onSkillSucc(succSkillList)


    def onCloneGM(self,exposedID,type):
        if exposedID != self.id:
            return
        if type == GmType.no_steal:
            self.gmNoSteal = True
        if type == GmType.shoot_fail:
            self.gmShootFail = True
        if type == GmType.shoot_succ:
            self.gmShootSucc = True




    def checkPassiveSkill(self):

        pass



class ActionTypeEnum:

    passBall = 1
    shoot = 2
    any = 3


class GmType:
    no_steal = 1
    shoot_succ = 2
    shoot_fail = 3




