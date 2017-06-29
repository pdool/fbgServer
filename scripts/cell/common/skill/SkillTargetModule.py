# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'

"""
获取技能使用的对象
(us 己方 enemy 对手  self 自身)
"""
# 后卫
guardPos = (2,3,4,5,6,7,8,9,10,11)
# 中场
midfieldPos = (8,7,10,12,13,14,15,16,18,19,20)
# 前锋
strikerPos = (17,18,19,20,21,22,23,24)



class SkillTargetModule:
    def __init__(self):
        pass


    def filterTarget(self,targetType):

        methodName = "filterTarget" + str(targetType)
        func = getattr(self,methodName)
        return  func()

    # 1、自身
    def filterTarget1(self):
        return (self.id,)
    # 2、对位防守者（不包括门将）
    def filterTarget2(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        defList = clone.getCurRoundDefList(clone.curPart)
        return defList
    # 3、对位进攻者
    def filterTarget3(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        curAttackID = clone.getCurRoundAtkId(clone.curPart)
        return (curAttackID,)

    # 4、对方门将
    def filterTarget4(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        # TODO:记得检查为什么不亮起来
        ERROR_MSG("controllerID  is " +str(clone.controllerID) + "   defenderID  is "+ str(clone.defenderID))
        if self.controllerID == clone.controllerID:
            enemyID = clone.defenderID
        else:
            enemyID = clone.controllerID
        if enemyID != -1:
            print(enemyID)
        ERROR_MSG("self id  is " + str(self.id) + "   enemyid  is " + str(enemyID))
        enemy = KBEngine.entities.get(enemyID)
        return (enemy.keeperID,)

    # 5、本队队友（含门将,不包含自己）
    def filterTarget5(self):
        controllerID = self.controllerID
        controller = KBEngine.entities.get(controllerID)
        teamMate = [cardId for cardId in controller.inTeamcardIDList if cardId != self.id]
        return teamMate

    # 6、本队门将
    def filterTarget6(self):
        controllerID = self.controllerID
        controller = KBEngine.entities.get(controllerID)
        return (controller.keeperID,)
    # 7、本队后卫

    def filterTarget7(self):
        controllerID = self.controllerID
        controller = KBEngine.entities.get(controllerID)

        guardList = []
        for id in controller.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            pos = card.pos
            if pos in guardPos:
                guardList.append(card.id)
        return guardList

    # 8、本队中场

    def filterTarget8(self):
        controllerID = self.controllerID
        controller = KBEngine.entities.get(controllerID)

        midfieldList = []
        for id in controller.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            pos = card.pos
            if pos in midfieldPos:
                midfieldList.append(card.id)
        return midfieldList
    # 本队前锋

    def filterTarget9(self):
        controllerID = self.controllerID
        controller = KBEngine.entities.get(controllerID)

        strikerList = []
        for id in controller.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            pos = card.pos
            if pos in strikerPos:
                strikerList.append(card.id)
        return strikerList

    # 10、（下一轮）接球的队友
    def filterTarget10(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        # 不是自己攻击的时候下一轮的接球的人还不知道
        if self.controllerID != clone.controllerID:
            return ()
        # 如果是第三步的时候没有下一轮
        if clone.curPart == 3:
            return None
        attackId = clone.getCurRoundAtkId(clone.curPart + 1)
        return (attackId,)
    # 全队
    def filterTarget11(self):
        controller = KBEngine.entities.get(self.controllerID)
        return controller.inTeamcardIDList

    # 12、新增：（下一轮）接球的对手球员
    def filterTarget12(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        if self.controllerID == clone.controllerID:
            return ()
        attackId = clone.getCurRoundAtkId(clone.curPart + 1)
        return (attackId,)

    # 13、新增：持球者
    def filterTarget13(self):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        attackId = clone.getCurRoundAtkId(clone.curPart + 1)
        return (attackId,)
# 目标
class TargetEnum:
    # 1、自身
    target_self = 1
    # 2、对位防守者（不包括门将）
    target_enemy_defender = 2
    # 3、对位进攻者
    target_enemy_attacker = 3
    # 4、对方门将
    target_enemy_keeper = 4
    # 5、本队队友（含门将）
    target_teammate = 5
    # 6、本队门将
    target_us_keeper = 6
    # 7、本队后卫
    target_us_guard = 7
    # 8、本队中场
    target_midfield = 8
    # 9、本队前锋
    target_us_striker =9
    # 10、（下一轮）接球的队友
    target_us_next_attacker = 10
    # 11、全队
    target_all_teammate = 11

    # 12、新增：（下一轮）接球的对手球员
    target_enemy_next_attacker = 12