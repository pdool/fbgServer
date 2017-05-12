# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'

"""
检测 技能使用条件
(us 己方 enemy 对手  self 自身)
"""

class SkillConditionModule:
    # 禁区
    penaltyArea = (34, 35, 36, 44, 45, 46, 54, 55, 56)

    def __init__(self):

        pass

    def checkCondition(self,condition,result):
        return self.fitCondition(condition,result)

    def fitCondition(self,condition,result):
        methodName = "checkCondition" + str(condition)
        func = getattr(self,methodName)
        return  func(result)


    # 1、自己持球时
    def checkCondition1(self,result):
        if result != ConditionEnum.con_result_None:
            return False

        # ERROR_MSG("  checkCondition1     result " + str(result))
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        curAttackID = clone.getCurRoundAtkId(clone.curPart)

        # ERROR_MSG("curAttackID   is " + str(curAttackID) +"   myCardId  " + str(self.id))

        if curAttackID != self.id:
            return False

        return True
    # 2、本方进攻回合时
    def checkCondition2(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)

        if self.controllerID != clone.controllerID:
            return False
        return True
    # 3、自己防守时
    def checkCondition3(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)

        if self.controllerID != clone.defenderID:
            return False

        defList = clone.getCurRoundDefList(clone.curPart)
        if self.id in defList:
            return True
        return False

    # 4、对方进攻时
    def checkCondition4(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)

        if self.controllerID == clone.controllerID:
            return False
        return True

    # 5、队友一对一防守时（对方进攻，非技能持有者对位时）
    def checkCondition5(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        # 本方进攻，退出
        if self.controllerID == clone.controllerID:
            return False
        # 防守人员

        defList = clone.getCurRoundDefList(clone.curPart)

        if len(defList) != 1:
            return False

        if self.id in defList:
            return False
        return True

    # 6、比赛中任何回合(不要配就行了)
    def checkCondition6(self,result):
        return True


    # 8、遇到一人防守时
    def checkCondition8(self,result):
        if result != ConditionEnum.con_result_None:
            return False

        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        curAttackID = clone.getCurRoundAtkId(clone.curPart)

        if curAttackID != self.id:
            return False
        defList = clone.getCurRoundDefList(clone.curPart)
        if len(defList)  != 1:
            return False
        return True

    # 9、己方进攻发起者轮次
    def checkCondition9(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        if self.controllerID != clone.controllerID:
            return False
        if clone.curPart != 1:
            return False
        return True

    # 10、己方进攻中间这轮次
    def checkCondition10(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        if self.controllerID != clone.controllerID:
            return False
        if clone.curPart != 2:
            return False
        return True

    # 11、己方进攻终结者轮次
    def checkCondition11(self,result):
        if result != ConditionEnum.con_result_None:
            return False
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        if self.controllerID != clone.controllerID:
            return False
        if clone.curPart != 3:
            return False
        return True


    # 13、本方领先
    def checkCondition13(self,result):

        controller = KBEngine.entities.get(self.controllerID)
        roomID = self.roomID
        room = KBEngine.entities.get(roomID)
        myScore = controller.shootSucc

        enemyID = room.avatarAID
        if room.avatarAID == self.controllerID:
            enemyID = room.avatarBID
        enemy =   KBEngine.entities.get(enemyID)
        enemySocre = enemy.shootSucc

        if myScore > enemySocre:
            return True

        return False
    # 14、本方落后
    def checkCondition14(self,result):
        return not self.checkCondition13(result)

    # 单刀
    def checkCondition15(self,result):
        if result != ConditionEnum.con_result_None:
            return
        roomID = self.roomID
        room = KBEngine.entities.get(roomID)

        curPart = room.curPart

        controller = KBEngine.entities.get(room.defenderID)

        if len(controller.defList[curPart -1]) == 0:
                return True

        return False

    # 16、禁区外自己持球时
    def checkCondition16(self, result):
        if result != ConditionEnum.con_result_None:
            return False

        ERROR_MSG("  checkCondition1     result " + str(result))
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        curAttackID = clone.getCurRoundAtkId(clone.curPart)

        ERROR_MSG("curAttackID   is " + str(curAttackID) + "   myCardId  " + str(self.id))

        if curAttackID != self.id:
            return False

        attackCoordinate = clone.getCurRoundAtkCoordinate(clone.curPart)
        if attackCoordinate in self.penaltyArea:
            return True
        return False
    # 队友进攻时
    def checkCondition22(self, result):
        if result != ConditionEnum.con_result_None:
            return False

        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        if self.controllerID != clone.controllerID:
            return False

        attackID = clone.getCurRoundAtkId(clone.curPart)

        if attackID != self.id:
            return True
        return False







    # 113、射门成功
    def checkCondition113(self,result):
        if result == ConditionEnum.con_result_None:
            return  False
        if result != ConditionEnum.con_result_shoot_succ:
            return False
        if self.checkCondition2(ConditionEnum.con_result_None)  :
            return True
        return False



    # 114、射门失败
    def checkCondition114(self,result):
        ERROR_MSG("   checkCondition114   result   " + str(result))
        if result == ConditionEnum.con_result_None:
            return  False
        if result != ConditionEnum.con_result_shoot_fail:
            return False
        if self.checkCondition2(ConditionEnum.con_result_None) :
            return True
        return False

    # 115、普通传球
    def checkCondition115(self,result):
        if result == ConditionEnum.con_result_None:
            return  False
        if result != ConditionEnum.con_result_pass_succ:
            return False
        if self.checkCondition2(ConditionEnum.con_result_None) :
            return True
        return False
    # 116、完美传球
    def checkCondition116(self,result):
        if result == ConditionEnum.con_result_None:
            return  False
        if result != ConditionEnum.con_result_perfect_pass:
            return False
        if self.checkCondition2(ConditionEnum.con_result_None):
            return True
        return False

    # 117、被抢断
    def checkCondition117(self,result):
        if result == ConditionEnum.con_result_None:
            return  False
        if result != ConditionEnum.con_result_be_steal:
            return False
        if self.checkCondition2(ConditionEnum.con_result_None):
            return True
        return False

    # 118、 突破成功
    def checkCondition118(self, result):
        if result == ConditionEnum.con_result_shoot_succ or result == ConditionEnum.con_result_shoot_fail or result == ConditionEnum.con_result_pass_succ or result == ConditionEnum.con_result_perfect_pass:
            if self.checkCondition1(ConditionEnum.con_result_None) is True:
                return True
        return False

    # 118、 突破成功
    def checkCondition119(self, result):
        if result == ConditionEnum.con_result_be_steal or result == ConditionEnum.con_result_shoot_fail:
            if self.checkCondition1(ConditionEnum.con_result_None) is True:
                return True
        return False


# 释放条件
class ConditionEnum:

    # 1、自己持球时
    con_self_attack = 1
    # 2、本方进攻回合时
    con_us_attack = 2
    # 3、自己防守时
    con_self_defend = 3
    # 4、对方进攻时
    con_enemy_attack = 4
    # 5、队友一对一防守时（对方进攻，非技能持有者对位时）
    con_us_defend_except_me = 5
    # 6、比赛中任何回合
    con_any = 6
    # 7、本方领先情况下防守时
    con_score_lead_and_defend = 7
    # 8、遇到一人防守时
    con_one_defend = 8
    # 9、己方进攻发起者轮次
    con_us_first_step = 9
    # 10、己方进攻中间这轮次
    con_us_second_step = 10
    # 11、己方进攻终结者轮次
    con_us_third_step = 11
    # 本方领先
    con_score_lead = 13
    # 对方领先
    con_enemy_lead = 14
    # 单刀
    con_on_on_one = 15

    # 禁区外正面自己持球时
    con_penaltyArea_self_attack = 16

    # 队友进攻时
    con_us_except_me_attack = 22

    # ==================================================================================================================
    # 非结果型
    con_result_None = 112
    # 113、射门成功
    con_result_shoot_succ = 113
    # 114、射门失败
    con_result_shoot_fail = 114
    # 115、普通传球
    con_result_pass_succ = 115
    # 116、完美传球
    con_result_perfect_pass = 116
    # 117、被抢断
    con_result_be_steal = 117
    # 突破成功
    con_result_break_succ = 118
    # 未射门成功（防守成功）
    con_result_not_shoot_succ = 119

    # 120、被守门员抢断
    con_result_be_keeper_steal = 120
    # 121、补射成功
    con_result_reshoot_succ = 121
    # 122、补射失败
    con_result_reshoot_fail = 122
