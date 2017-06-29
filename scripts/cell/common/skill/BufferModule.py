# -*- coding: utf-8 -*-
import KBEngine
import skillConfig
import util
from Avatar import Avatar
from CommonEnum import LastRoundEnmu, ImpactTypeEnum
from KBEDebug import ERROR_MSG
from common.skill.SkillConditionModule import ConditionEnum
from common.skill.SkillEffectModule import EffectEnum

__author__ = 'chongxin'

class BufferModule:
    insideResult = {ConditionEnum.con_result_pass_succ, ConditionEnum.con_result_perfect_pass,
                    ConditionEnum.con_result_break_succ}
    def __init__(self):
        self.bufferContainer =[]
    # 增加一个buffer
    def addBuffer(self, targetID, subSkillID):

        subSkillConf = skillConfig.SkillConfig[subSkillID]
        controller = KBEngine.entities.get(self.controllerID)

        buffer = {
            "startType"         : subSkillConf["startType"],
            "lastRound"         : subSkillConf["lastRound"],
            "noticeClient"      : subSkillConf["noticeClient"],
            "subSkillID"        : subSkillID,
            "condition"          : subSkillConf["condition"]
        }
        # 免疫负面状态
        impactType = subSkillConf["impactType"]
        if self.immuneNegativeBuffer and impactType == ImpactTypeEnum.debuffs:
            return


        room = KBEngine.entities.get(self.roomID)
        isAttackRound = False
        if room.controllerID == self.controllerID:
            isAttackRound = True
        card = KBEngine.entities.get(targetID)
        noticeClient = subSkillConf["noticeClient"]

        ERROR_MSG("-----------addbuffer-----------targetID-----------  " + str(targetID) + "   subskillID    " + str(subSkillID))
        # 如果是结果型的加进去就行了
        if subSkillConf["condition"] != ConditionEnum.con_result_None:
            card.bufferContainer.append(buffer)

            ERROR_MSG("card.bufferContainer   cardID is   " +str(card.id)+"       " + card.bufferContainer.__str__())
            return

        if isinstance(controller, Avatar) and noticeClient == 1:
            controller.client.onAddBuffer(targetID, subSkillID)
        # 如果是立即生效的看 startType
        targetList = [self.id]
        startType = subSkillConf["startType"]

        if  startType == StartTypeEnmu.cur_round:
            self.makeEffect(targetList,subSkillConf)

            if subSkillConf["lastRound"] > 1:
                buffer["lastRound"]  = subSkillConf["lastRound"] - 1
                card.bufferContainer.append(buffer)
        elif startType == StartTypeEnmu.cur_round_and_attack_round:
            if isAttackRound:
                self.makeEffect(targetList, subSkillConf)
                if subSkillConf["lastRound"] > 1:
                    buffer["lastRound"] = subSkillConf["lastRound"] - 1
                    card.bufferContainer.append(buffer)
        elif startType == StartTypeEnmu.cur_round_and_defend_round:
            if not isAttackRound:
                self.makeEffect(targetList, subSkillConf)

                if subSkillConf["lastRound"] > 1:
                    buffer["lastRound"] = subSkillConf["lastRound"] - 1
                    card.bufferContainer.append(buffer)
        else:
            card.bufferContainer.append(buffer)

            ERROR_MSG("card.bufferContainer   cardID is   " + str(card.id) + "       " + card.bufferContainer.__str__())



    # 开始一轮之前(中间步骤也会启动。结束也会启动)
    def bufferEffect(self,result = ConditionEnum.con_result_None):
        room = KBEngine.entities.get(self.roomID)
        isAttackRound =False
        if room.controllerID == self.controllerID:
            isAttackRound = True

        for i in range(len(self.bufferContainer) - 1, -1, -1):
            buffer = self.bufferContainer[i]
            statrType = buffer["startType"]
            targetList = [self.id]
            subSkillID = buffer["subSkillID"]
            condition = buffer["condition"]
            noticeClient = buffer["noticeClient"]
            controller = KBEngine.entities.get(self.controllerID)

            subSkillConf = skillConfig.SkillConfig[subSkillID]
            # 1、一轮之前
            if condition ==  ConditionEnum.con_result_None:
                if isAttackRound:
                    if statrType == StartTypeEnmu.cur_round_and_attack_round or statrType == StartTypeEnmu.next_round_attack_round or statrType == StartTypeEnmu.cur_round:
                        self.makeEffect(targetList, subSkillConf)
                        self.bufferAfterUse(i)
                else:
                    if statrType == StartTypeEnmu.cur_round_and_defend_round or statrType == StartTypeEnmu.next_round_defend_round or statrType == StartTypeEnmu.cur_round:
                        self.makeEffect(targetList, subSkillConf)
                        self.bufferAfterUse(i)
                pass
            # 2、一轮之后
            else:
                ERROR_MSG(" bufferEffect result    is    "+ str(result))
                if condition == ConditionEnum.con_result_shoot_succ:
                    # 如果是内部结果直接pass
                    if result in self.insideResult:
                        continue
                    # 门柱保命
                    if subSkillID //10000 == 1036:
                        #     防守回合
                        self.skill1036Effect(buffer)
                        continue

                    if result != condition:
                        self.bufferContainer.pop(i)
                    else:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)

                elif condition == ConditionEnum.con_result_shoot_fail:
                    # 如果是内部结果直接pass
                    if result in self.insideResult:
                        continue
                    if result != condition:
                        self.bufferContainer.pop(i)
                    else:
                        # 激活下次不检查了 TODO:通知另外一个人
                        buffer["condition"] = ConditionEnum.con_result_None

                        if subSkillID // 1000 == 1004:
                            self.addEffect28(subSkillID, 28, None,None,[self.id])

                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)

                elif condition == ConditionEnum.con_result_be_steal:
                    # 如果是内部结果直接pass
                    if result in self.insideResult:
                        continue
                    if result != condition:
                        self.bufferContainer.pop(i)
                    else:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)

                elif condition == ConditionEnum.con_result_not_shoot_succ:
                    # 如果是内部结果直接pass
                    if result in self.insideResult:
                        continue

                    if result == ConditionEnum.con_result_shoot_fail or result == ConditionEnum.con_result_not_shoot_succ:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)
                    else:
                        self.bufferContainer.pop(i)


                # 中间结果
                elif condition == ConditionEnum.con_result_pass_succ:
                    if result == ConditionEnum.con_result_be_steal:
                        self.bufferContainer.pop(i)
                    else:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)
                elif condition == ConditionEnum.con_result_perfect_pass:
                    if result != ConditionEnum.con_result_perfect_pass:
                        self.bufferContainer.pop(i)
                    else:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)
                elif condition == ConditionEnum.con_result_break_succ:
                    if result != ConditionEnum.con_result_be_steal:
                        # 激活下次不检查了
                        buffer["condition"] = ConditionEnum.con_result_None
                        if isinstance(controller, Avatar) and noticeClient == 1:
                            controller.client.onAddBuffer(self.id, subSkillID)
                    else:
                        self.bufferContainer.pop(i)


    # 使用完之后减少持续轮数
    def bufferAfterUse(self, i):
        # 倒序删除
        buffer = self.bufferContainer[i]
        lastRound = buffer["lastRound"]
        # 1、处理轮数

        if lastRound > 0:
            if lastRound -1 <= 0:
                self.delBuffer(i)
                self.bufferContainer.pop(i)
                self.delLastEffect(buffer)

            else:
                buffer["lastRound"] = lastRound -1
        # TODO:半场全场处理
        # else:
        #     if lastRound == LastRoundEnmu.firstHalf:
        #     pass


    def delBuffer(self,i):
        buffer = self.bufferContainer[i]
        subSkillID = buffer["subSkillID"]
        subSkillConf = skillConfig.SkillConfig[subSkillID]
        controller = KBEngine.entities.get(self.controllerID)

        ERROR_MSG("delBuffer   cardID is " + str(self.id) + "       buffer    "+ buffer.__str__())

        ERROR_MSG(util.printStackTrace("delBuffer      "))

        noticeClient = subSkillConf["noticeClient"]
        if isinstance(controller, Avatar) and noticeClient == 1:
            controller.client.onDelBuffer(self.id, subSkillID)


class StartTypeEnmu:
    # 当前回合（下一个回合进攻和防守都生效，回合开始时）
    cur_round = 1
    # 当前回合启动，进攻回合生效
    cur_round_and_attack_round = 2
    # 当前回合启动，防守回合生效
    cur_round_and_defend_round = 3
    # 下一回合启动，进攻回合生效
    next_round_attack_round = 4
    # 下一回合启动，防守回合生效
    next_round_defend_round = 5
    # 回合结束后处理（下一个回合进攻和防守都生效）
    end_round = 6

