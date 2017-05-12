# -*- coding: utf-8 -*-
import KBEngine
import effectConfig
import skillConfig
import util
from Avatar import Avatar
from CommonEnum import ImpactTypeEnum, PlayerOp
from KBEDebug import ERROR_MSG

__author__ = 'chongxin'

class SkillEffectModule:
    def __init__(self):
        pass


    def makeEffect(self,targetList,subSkillID):

        config = skillConfig.SkillConfig[subSkillID]

        if config["effectType1"] != 0:
            effctType1 = config["effectType1"]
            valueType1 = config["valueType1"]
            value1 = config["value1"]

            methodName = "addEffect" + str(effctType1)
            func = getattr(self, methodName)
            func(subSkillID,effctType1,valueType1,value1,targetList)

        if config["effectType2"] != 0:
            effctType2 = config["effectType2"]
            valueType2 = config["valueType2"]
            value2 = config["value2"]

            methodName = "addEffect" + str(effctType2)
            func = getattr(self, methodName)
            func(subSkillID,effctType2,valueType2, value2, targetList)

        if config["effectType3"] != 0:
            effctType3 = config["effectType3"]
            valueType3 = config["valueType3"]
            value3 = config["value3"]

            methodName = "addEffect" + str(effctType3)
            func = getattr(self, methodName)
            func(subSkillID,effctType3,valueType3, value3, targetList)

    # 1、射门值、射门值 %
    def addEffect1(self,subSkillID,effectType,valueType,value,targetList):
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            if valueType == ValueTypeEnmu.value:
                card.shootSkillValue = card.shootSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.shootSkillPer = card.shootSkillPer + value /1000.0

            self.noticeClientEffect(subSkillID, cardId, effectType)
            ERROR_MSG("addEffect1   cardID  is  " + str(cardId) + "    value is   " + str(value) + " shootSkillPer " + str(card.shootSkillPer))
# 2、传球值、传球值 %
    def addEffect2(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect2  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.passballSkillValue = card.passballSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.passballSkillPer = card.passballSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 3、盘带值、盘带值 %
    def addEffect3(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect3  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.reelSkillValue = card.reelSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.reelSkillPer = card.reelSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)

    # 4、控球值、控球值 %（增加控球值效果的技能都是被动，在计算攻守回合数时就要计算进去）
    def addEffect4(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect4  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.controllSkillValue = card.controllSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.controllSkillPer = card.controllSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)

    # 5、防守值、防守值 %
    def addEffect5(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect5  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.defendSkillValue = card.defendSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.defendSkillPer = card.defendSkillPer + value  /1000.0

            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 6、拦截值、拦截值 %
    def addEffect6(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect6  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.trickSkillValue = card.trickSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.trickSkillPer = card.trickSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 7、抢断值、抢断值 %
    def addEffect7(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect7  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.stealSkillValue = card.stealSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.stealSkillPer = card.stealSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 8、守门值、守门值 %
    def addEffect8(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect8  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if valueType == ValueTypeEnmu.value:
                card.keepSkillValue = card.keepSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.keepSkillPer = card.keepSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 9、射偏率
    def addEffect9(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect9  cardID  is  " + str(cardId) + "    value is   " + str(value))

            card.shootMissSkillPer = card.shootMissSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 10、进球率（计算完 （射门值 - 防守值） / 守门值的值）
    def addEffect10(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect10  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.shootSuccSkillPer = card.shootSuccSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 11、过人成功率（计算完 （抢断值 - 盘带值） / 抢断基数的值）
    def addEffect11(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect11  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.breakthroughSkillPer = card.breakthroughSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 12、完美传球几率（计算完 （传球 - 拦截） / 传球基数的值）
    def addEffect12(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect12  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.perfectPassballSkillPer = card.perfectPassballSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 13、怒气值
    def addEffect13(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect13  cardID  is  " + str(cardId) + "    value is   " + str(value))
            if hasattr(card, "anger") is False:
                card.anger = 0
            card.anger = card.anger + value
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 14、终结者计算得球概率提升
    # 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
    # ca1*p%/(ca1*p%+ca2+……caN)
    def addEffect14(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect14  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.thirdStepAttackSkillPer = card.thirdStepAttackSkillPer + value /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)

    # 15、中间者计算得球概率提升
    # 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
    # ca1*p%/(ca1*p%+ca2+……caN)
    def addEffect15(self,subSkillID,effectType,valueType,value,targetList):

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            ERROR_MSG("addEffect15  cardID  is  " + str(cardId) + "    value is   " + str(value))
            card.secondStepAttackSkillPer = card.secondStepAttackSkillPer + value  /1000.0
            self.noticeClientEffect(subSkillID, cardId, effectType)
    # 16、将A属性的值或n % 的值，附加到B的属性上
    def addEffect16(self,subSkillID,effectType,valueType,value,targetList):
        pass

    # 17、造成晕眩，无法进行防守
    def addEffect17(self,subSkillID,effectType,valueType,value,targetList):
        # 无法参与防守(不计算进攻和防守)
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            card.unableDefend = True
            self.noticeClientEffect(subSkillID, cardId, effectType)


    # 18、获得黄牌
    def addEffect18(self,subSkillID,effectType,valueType,value,targetList):

        room = KBEngine.entities.get(self.roomID)
        a = KBEngine.entities.get(room.avatarAID)
        b = KBEngine.entities.get(room.avatarBID)

        if self.controllerID == a.id:
            controller = a
        else:
            controller = b

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)

            card.yellow = card.yellow + 1
            if a.typeStr == "Avatar":
                a.client.onYellowCard(cardId)
            if b.typeStr == "Avatar":
                b.client.onYellowCard(cardId)
            if card.yellow == 2:
                card.red = 1
                card.yellow = 0
                controller.inTeamcardIDList.remove(self.id)
                if a.typeStr == "Avatar":
                    a.client.onRedCard(cardId)
                if b.typeStr == "Avatar":
                    b.client.onRedCard(cardId)



    # 19、获得红牌
    def addEffect19(self,subSkillID,effectType,valueType,value,targetList):
        room = KBEngine.entities.get(self.roomID)
        a = KBEngine.entities.get(room.avatarAID)
        b = KBEngine.entities.get(room.avatarBID)

        if self.controllerID == a.id:
            controller = a
        else:
            controller = b

        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            card.red = 1
            controller.inTeamcardIDList.remove(self.id)

            if a.typeStr == "Avatar":
                a.client.onRedCard(cardId)
            if b.typeStr == "Avatar":
                b.client.onRedCard(cardId)





    # 22、意识传递（主\攻击回合）：将自身射门值n%加成在传球值上，持续3个进攻回合
    def addEffect22(self,subSkillID,effectType,valueType,value,targetList):
        for cardId in targetList:
            card = KBEngine.entities.get(cardId)
            if valueType == ValueTypeEnmu.value:
                card.passballSkillValue = card.shootSkillValue + value
            elif valueType == ValueTypeEnmu.percent:
                card.passballSkillValue = card.shootSkillValue + value  /1000.0
            self.noticeClientEffect(subSkillID,cardId,effectType)

    # 终止一个回合
    def addEffect23(self,subSkillID,effectType,valueType,value,targetList):
        roomID = self.roomID
        clone = KBEngine.entities.get(roomID)
        clone.endRound = True

        self.noticeClientEffect(subSkillID, self.id, effectType)

    # 24 协防补位（一对一防守时）
    def addEffect24(self,subSkillID,effectType,valueType,value,targetList):
        roomID = self.roomID
        room = KBEngine.entities.get(roomID)

        defList = room.getCurRoundDefList(room.curPart)

        defList.append(self.id)

        self.noticeClientEffect(subSkillID,self.id,effectType)



    # 25、#免疫负面状态（不再获得负面状态，已有的还存在
    def addEffect25(self,subSkillID,effectType,valueType, value, targetList):
        self.immuneNegativeBuffer = True

    # 26、解除负面状态（解除身上已拥有的负面状态，不免疫本轮获取的负面状态）
    def addEffect26(self,subSkillID,effectType,valueType, value, targetList):
        for i in range(len(self.bufferContainer) - 1, -1, -1):
            buffer = self.bufferContainer[i]
            subSkillID = buffer["subSkillID"]
            skillConf = skillConfig.SkillConfig[subSkillID]
            impactType = skillConf["impactType"]

            if impactType == ImpactTypeEnum.debuffs:
                self.bufferContainer.pop(i)


    # 补射
    def addEffect28(self,subSkillID,effectType,valueType, value, targetList):
        room = KBEngine.entities.get(self.roomID)
        # 补射
        room.reShootCardID = self.id
        room.endRound = False

        ERROR_MSG(util.printStackTrace("addEffect28 reshoot      "))
        room.onCmdSelectSkill(PlayerOp.shoot)

    # 防守反击
    def addEffect29(self,subSkillID,effectType,valueType, value, targetList):
        room = KBEngine.entities.get(self.roomID)
        controllerID = room.controllerID
        bID = room.avatarBID

        ERROR_MSG("addEffect29                                                    chongxin")


        # 现在攻击的人是b
        curAttackIndex = room.curAttackIndex + 1
        if bID == controllerID:
            if curAttackIndex in room.bAttackList:
        #         调整
                room.bAttackList.remove(curAttackIndex)
                for x in range(curAttackIndex + 1,room.totalAttackTimes):
                    if x not in room.bAttackList:
                        room.append(x)
                        break
        else:
            # 如果下一轮攻击不是B调整为B
            if curAttackIndex not in room.bAttackList:
                room.bAttackList.append(curAttackIndex)
                room.pop(len(room.bAttackList)-1)

        self.noticeClientEffect(subSkillID,self.id,effectType)


    # 删除技能效果
    def delLastEffect(self, buffer):
        subSkill = buffer["subSkillID"]
        subSkillConf = skillConfig.SkillConfig[subSkill]
        effectType1 = subSkillConf["effectType1"]
        effectType2 = subSkillConf["effectType2"]
        effectType3 = subSkillConf["effectType3"]

        self.delEffect(effectType1)
        self.delEffect(effectType2)
        self.delEffect(effectType3)

    def delEffect(self,effectType):

        if effectType == EffectEnum.effect_no_defend:
            self.unableDefend = False

        elif effectType == EffectEnum.effect_immune_negative_buffer:

            self.immuneNegativeBuffer = False

    def noticeClientEffect(self,subSkill,cardID,effectType):
        room = KBEngine.entities.get(self.roomID)
        avatarA = KBEngine.entities.get(room.avatarAID)
        avatarB = KBEngine.entities.get(room.avatarBID)

        # ERROR_MSG("noticeClientResult    " + str(self.roundResult))

        if isinstance(avatarA, Avatar):
            avatarA.client.noticeClientEffect(cardID,subSkill//10000,effectType)

        if isinstance(avatarB, Avatar):
            avatarB.client.noticeClientEffect(cardID,subSkill//10000,effectType)



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

    # ===================================================
    # 13、怒气值
    effect_add_anger = 13
    # ===================================================

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


    # 将自身射门值的n%加到传球值上
    effect_1005_effect = 22
    # 结束回合
    effect_end_round = 23
    # 协防补位
    effect_help_defend = 24
    #免疫负面状态（不再获得负面状态，已有的还存在
    effect_immune_negative_buffer = 25
    #26、解除负面状态（解除身上已拥有的负面状态，不免疫本轮获取的负面状态）
    effect_del_negative_buffer = 26

    # 补射一次
    effect_reshoot = 28

    # 反击
    effect_counterattack = 29



class ValueTypeEnmu:
    # 数值
    value = 0
    # 百分比
    percent = 1