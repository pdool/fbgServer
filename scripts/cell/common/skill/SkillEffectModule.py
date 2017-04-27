# -*- coding: utf-8 -*-
import KBEngine
import effectConfig
import skillConfig
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'

class SkillEffectModule:
    def __init__(self):

        self.__funcMap = {
            EffectEnum.effect_add_shoot:                    self.addEffect1,
            EffectEnum.effect_add_passball:                 self.addEffect2,
            EffectEnum.effect_add_reel:                     self.addEffect3,
            EffectEnum.effect_add_control:                  self.addEffect4,
            EffectEnum.effect_add_defend:                   self.addEffect5,
            EffectEnum.effect_add_trick:                    self.addEffect6,
            EffectEnum.effect_add_steal:                    self.addEffect7,
            EffectEnum.effect_add_keep:                     self.addEffect8,
            EffectEnum.effect_add_shoot_miss_per:           self.addEffect9,
            EffectEnum.effect_shoot_succ_per:               self.addEffect10,
            EffectEnum.effect_breakthrough_per:             self.addEffect11,
            EffectEnum.effect_perfect_passball_per:         self.addEffect12,
            EffectEnum.effect_add_anger:                    self.addEffect13,
            EffectEnum.effect_as_third_step_player_per:     self.addEffect14,
            EffectEnum.effect_as_second_step_player_per:    self.addEffect15,
            EffectEnum.effect_remove_a_add_b:               self.addEffect16,
            EffectEnum.effect_no_defend:                    self.addEffect17,
            EffectEnum.effect_get_yellow:                   self.addEffect18,
            EffectEnum.effect_get_red:                      self.addEffect19,
            EffectEnum.effect_change_flow:                  self.addEffect20,
            EffectEnum.effect_1005_effect:                  self.addEffect22,
            EffectEnum.effect_end_round:                    self.addEffect23,
        }

        pass

    def makeEffect(self,targetList,subSkillID):

        config = skillConfig.SkillConfig[subSkillID]

        if config["effectType1"] != 0:
            effctType1 = config["effectType1"]
            valueType1 = config["valueType1"]
            value1 = config["value1"]

            func = self.__funcMap[effctType1]
            func(valueType1,value1,targetList)

        if config["effectType2"] != 0:
            effctType2 = config["effectType2"]
            valueType2 = config["valueType2"]
            value2 = config["value2"]

            func = self.__funcMap[effctType2]
            func(valueType2,value2,targetList)

        if config["effectType3"] != 0:
            effctType3 = config["effectType3"]
            valueType3 = config["valueType3"]
            value3 = config["value3"]

            func = self.__funcMap[effctType3]
            func(valueType3,value3,targetList)

    # 1、射门值、射门值 %
    def addEffect1(self,valueType,value,targetList):
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            if valueType == ValueTypeEnmu.value:
                card.shootSkillValue = card.shootSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.shootSkillPer = card.shootSkillPer + value /1000.0

            ERROR_MSG("addEffect1   cardID  is  " + str(cardId) + "    value is   " + str(value) + " shootSkillPer " + str(card.shootSkillPer))
# 2、传球值、传球值 %
    def addEffect2(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect2  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.passballSkillValue = card.passballSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.passballSkillPer = card.passballSkillPer + value  /1000.0

    # 3、盘带值、盘带值 %
    def addEffect3(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect3  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.reelSkillValue = card.reelSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.reelSkillPer = card.reelSkillPer + value  /1000.0

    # 4、控球值、控球值 %（增加控球值效果的技能都是被动，在计算攻守回合数时就要计算进去）
    def addEffect4(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect4  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.controllSkillValue = card.controllSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.controllSkillPer = card.controllSkillPer + value  /1000.0

    # 5、防守值、防守值 %
    def addEffect5(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect5  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.defendSkillValue = card.defendSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.defendSkillPer = card.defendSkillPer + value  /1000.0

    # 6、拦截值、拦截值 %
    def addEffect6(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect6  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.trickSkillValue = card.trickSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.trickSkillPer = card.trickSkillPer + value  /1000.0

    # 7、抢断值、抢断值 %
    def addEffect7(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect7  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.stealSkillValue = card.stealSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.stealSkillPer = card.stealSkillPer + value  /1000.0

    # 8、守门值、守门值 %
    def addEffect8(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect8  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.keepSkillValue = card.keepSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.keepSkillPer = card.keepSkillPer + value  /1000.0

    # 9、射偏率
    def addEffect9(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect9  cardID  is  " + str(cardId) + "    value is   " + str(value))

            card.shootMissSkillPer = card.shootMissSkillPer + value  /1000.0

    # 10、进球率（计算完 （射门值 - 防守值） / 守门值的值）
    def addEffect10(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect10  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.shootSuccSkillPer = card.shootSuccSkillPer + value  /1000.0

    # 11、过人成功率（计算完 （抢断值 - 盘带值） / 抢断基数的值）
    def addEffect11(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect11  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.breakthroughSkillPer = card.breakthroughSkillPer + value  /1000.0

    # 12、完美传球几率（计算完 （传球 - 拦截） / 传球基数的值）
    def addEffect12(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect12  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.perfectPassballSkillPer = card.perfectPassballSkillPer + value  /1000.0

    # 13、怒气值
    def addEffect13(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect13  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if hasattr(card, "anger") is False:
                card.anger = 0
            card.anger = card.anger + value

    # 14、终结者计算得球概率提升
    # 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
    # ca1*p%/(ca1*p%+ca2+……caN)
    def addEffect14(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect14  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.thirdStepAttackSkillPer = card.thirdStepAttackSkillPer + value /1000.0


    # 15、中间者计算得球概率提升
    # 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
    # ca1*p%/(ca1*p%+ca2+……caN)
    def addEffect15(self,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect15  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.secondStepAttackSkillPer = card.secondStepAttackSkillPer + value  /1000.0

    # 16、将A属性的值或n % 的值，附加到B的属性上
    def addEffect16(self,valueType,value,targetList):
        pass

    # 17、造成晕眩，无法进行防守
    def addEffect17(self,valueType,value,targetList):
        pass

    # 18、获得黄牌
    def addEffect18(self,valueType,value,targetList):
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)

            card.yellow = card.yellow + 1
            if card.yellow == 2:
                card.red = 1
                card.yellow = 0

                controller = KBEngine.entities.get(self.controllerID)
                controller.inTeamcardIDList.remove(self.id)

    # 19、获得红牌
    def addEffect19(self,valueType,value,targetList):
        controller = KBEngine.entities.get(self.controllerID)
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            card.red = 1
            controller.inTeamcardIDList.remove(self.id)


    # 20、改变流程
    def addEffect20(self,valueType,value,targetList):
        pass

    # 21、加buffer
    # def addEffect21(self,valueType,value,targetList):
    #     bufferID = effectCon["value"]
    #     for cardId in targetList:
    #         card = KBEngine.entities.get(cardId)
    #         ERROR_MSG("addEffect21  cardID  is  " + str(cardId) + "    value is   " + str(bufferID))
    #         card.addBuffer(bufferID)

    # 22、意识传递（主\攻击回合）：将自身射门值n%加成在传球值上，持续3个进攻回合
    def addEffect22(self,valueType,value,targetList):
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            if valueType == ValueTypeEnmu.value:
                card.passballSkillValue = card.shootSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.passballSkillValue = card.shootSkillValue + value  /1000.0

    # 终止一个回合
    def addEffect23(self,valueType,value,targetList):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        clone.endRound = True

    # 协防补位（一对一防守时）
    def addEffect24(self,valueType,value,targetList):
        roomID = self.roomID
        room = KBEngine.entities.get(roomID)

        defList = room.getCurRoundDefList(room.curPart)

        if self.id in defList:
            return

        defList.append(self.id)


# 效果类型
class EffectEnum:

    # 1、射门值、射门值 %
    effect_add_shoot = 1
    # 2、传球值、传球值 %
    effect_add_passball = 2
    # 3、盘带值、盘带值 %
    effect_add_reel = 3
    # 4、控球值、控球值 %（增加控球值效果的技能都是被动，在计算攻守回合数时就要计算进去）
    effect_add_control = 4
    # 5、防守值、防守值 %
    effect_add_defend = 5
    # 6、拦截值、拦截值 %
    effect_add_trick = 6
    # 7、抢断值、抢断值 %
    effect_add_steal = 7
    # 8、守门值、守门值 %
    effect_add_keep = 8
    # 9、射偏率
    effect_add_shoot_miss_per = 9
    # 10、进球率（计算完 （射门值 - 防守值） / 守门值的值）
    effect_shoot_succ_per = 10
    # 11、过人成功率（计算完 （抢断值 - 盘带值） / 抢断基数的值）
    effect_breakthrough_per = 11
    # 12、完美传球几率（计算完 （传球 - 拦截） / 传球基数的值）
    effect_perfect_passball_per = 12

    # 14、终结者计算得球概率提升
    effect_as_third_step_player_per = 14
    # 15、中间者计算得球概率提升
    effect_as_second_step_player_per = 15
    # 16、将A属性的值或n % 的值，附加到B的属性上
    effect_remove_a_add_b = 16
    # 17、造成晕眩，无法进行防守
    effect_no_defend = 17
    # 18、获得黄牌
    effect_get_yellow = 18
    # 19、获得红牌
    effect_get_red = 19
    # 20、改变流程
    effect_change_flow = 20
    # 21、加buffer
    effect_add_buffer = 21
    # ===================================================
    # 13、怒气值
    effect_add_anger = 13
    # ===================================================

    # 将自身射门值的n%加到传球值上
    effect_1005_effect = 22
    # 结束回合
    effect_end_round = 23



class ValueTypeEnmu:
    # 数值
    value = 0
    # 百分比
    percent = 1