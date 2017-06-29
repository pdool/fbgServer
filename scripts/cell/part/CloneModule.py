# -*- coding: utf-8 -*-
from CommonEnum import PlayerOp, ActionTypeEnum
from ErrorCode import SkillModuleError
from KBEDebug import *
from common.skill.SkillConditionModule import ConditionEnum

__author__ = 'chongxin'
__createTime__  = '2017年2月15日'
"""
副本模块
"""

class CloneModule:

    def __init__(self):

        if self.actionType == ActionTypeEnum.action_clone:
            print(" avatar clone init -------------------------")
            self.client.onReady()
        if self.actionType == ActionTypeEnum.official_promotion or self.actionType == ActionTypeEnum.action_arena:
            print(" avatar clone init -------------------------")
            self.client.onReady()
        if self.actionType == ActionTypeEnum.league_clone or self.actionType == ActionTypeEnum.league_player:
            print(" avatar clone init -------------------------")
            self.client.onReady()




    # 客户端通知开始战斗

    def onClientBeginFight(self,exposedID):
        if exposedID != self.id:
            return
        roomID = self.roomID

        room = KBEngine.entities.get(roomID)

        print(" avatar  onClientBeginFight -------------------------")
        room.setReadyState(self.id)

        self.client.onMyCardIdList(self.inTeamcardIDList)


    def onClientPlayAnimFinish(self,exposedID):
        if exposedID != self.id:
            return

        WARNING_MSG("onClientPlayAnimFinish")
        cloneID = self.roomID

        room = KBEngine.entities.get(cloneID)
        room.onCmdPlayAnimFinish(self.id)

    def onClientSelectOp(self,exposedID,op ,leftSkillIdList,rightSkillIdList):
        if exposedID != self.id:
            return
        WARNING_MSG("onClientSelectOp   " + str(op))
        for cardId in leftSkillIdList:
            ERROR_MSG("-----------onClientSelectOp-----------------cardId-----------  " + str(cardId))

        cloneID = self.roomID
        room = KBEngine.entities.get(cloneID)

        if room.controllerID == self.id and op == PlayerOp.defendOp:
            self.client.onSkillError(SkillModuleError.worong_op)
            ERROR_MSG( " self is atcker but op is defend")
            return
        elif room.defenderID == self.id and op != PlayerOp.defendOp:
            self.client.onSkillError(SkillModuleError.worong_op)
            ERROR_MSG(" self is defender but op not is defend")
            return

        if op != PlayerOp.defendOp:
            # 1、检查基础操作actionType是不是对的
            if room.curPart == 1 and op != PlayerOp.passball:
                self.client.onSkillError(SkillModuleError.worong_op)
                WARNING_MSG("onClientSelectOp  1")
                return
            if room.curPart == 2:
                if op != PlayerOp.passball and op != PlayerOp.shoot:
                    self.client.onSkillError(SkillModuleError.worong_op)
                    WARNING_MSG("onClientSelectOp  2")
                    return

            if room.curPart == 3 and op != PlayerOp.shoot:
                self.client.onSkillError(SkillModuleError.worong_op)
                WARNING_MSG("onClientSelectOp  3")
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

        result = ConditionEnum.con_result_None
        succSkillList = []
        for cardId in leftSkillIdList:
            card = KBEngine.entities.get(cardId)

            mainSkill = card.skill1_B

            skillLevel =  card.skill1_Level

            ERROR_MSG(" skill1_b  " + str(card.skill1_B))

            card.useSkill(mainSkill,skillLevel,result)

            succSkillList.append(mainSkill)

        room.setSelectState(self.id,op)



        #
        # succ = "succSkillList ==========="
        # for ski in succSkillList:
        #     succ = succ + str(ski)
        # ERROR_MSG(succ)
        #
        ERROR_MSG("succSkillList        " + succSkillList.__str__())
        self.client.onSkillSucc(succSkillList)


    def onCloneGM(self,exposedID,type):
        if exposedID != self.id:
            return

        room = KBEngine.entities.get(self.roomID)
        if type == GmType.no_steal:
            room.gmNoSteal = True
            ERROR_MSG(" onCloneGM   no steal  ")
        if type == GmType.shoot_fail:
            room.gmShootFail = True
            ERROR_MSG(" onCloneGM   shoot    fail  ")
        if type == GmType.shoot_succ:
            room.gmShootSucc = True
            ERROR_MSG(" onCloneGM   shoot    succ  ")

    def onGmSetSkill(self,exposedID,skillID):

        for id in self.inTeamcardIDList:
            card = KBEngine.entities.get(id)

            card.skill1_B = skillID

        ERROR_MSG("  setGmSkillID  " + str(skillID))

    def checkPassiveSkill(self):

        pass


#
# class ActionTypeEnum:
#
#     passBall = 1
#     shoot = 2
#     any = 3


class GmType:
    no_steal = 1
    shoot_succ = 2
    shoot_fail = 3
    set_skill = 4




