# -*- coding: utf-8 -*-
import KBEngine
import skillConfig
from Avatar import Avatar
from KBEDebug import ERROR_MSG
from common.skill.SkillConditionModule import ConditionEnum

__author__ = 'chongxin'

class BufferModule:
    def __init__(self):
        self.bufferContainer =[]
        pass
    # 增加一个buffer
    def addBuffer(self, targetList, subSkillID):

        subSkillConf = skillConfig.SkillConfig[subSkillID]
        controller = KBEngine.entities.get(self.controllerID)

        buffer = {
            "startType"         : subSkillConf["startType"],
            "lastRound"         : subSkillConf["lastRound"],
            "noticeClient"      : subSkillConf["noticeClient"],
            "subSkillID"        : subSkillID,
            "condition"          : subSkillConf["condition"]
        }

        room = KBEngine.entities.get(self.roomID)
        isAttackRound = False
        if room.controllerID == self.controllerID:
            isAttackRound = True
        for target in targetList:
            card = KBEngine.entities.get(target)
            noticeClient = subSkillConf["noticeClient"]
            ERROR_MSG("-----------addbuffer-----------targetID-----------------  " + str(target))

            # if isinstance(controller,Avatar) and noticeClient == 1:
            #     controller.client.onAddBuffer(target,subSkillID)
            # 如果是结果型的加进去就行了
            if subSkillConf["condition"] != ConditionEnum.con_result_None:
                card.bufferContainer.append(buffer)

                continue

            # 如果是立即生效的看 startType
            targetList = [self.id]
            startType = subSkillConf["startType"]

            if  startType == StartTypeEnmu.cur_round:
                self.makeEffect(targetList,subSkillID)

                if subSkillConf["lastRound"] > 1:
                    buffer["lastRound"]  = subSkillConf["lastRound"] - 1
                    card.bufferContainer.append(buffer)
            elif startType == StartTypeEnmu.cur_round_and_attack_round:
                if isAttackRound:
                    self.makeEffect(targetList, subSkillID)
                    if subSkillConf["lastRound"] > 1:
                        buffer["lastRound"] = subSkillConf["lastRound"] - 1
                        card.bufferContainer.append(buffer)
            elif startType == StartTypeEnmu.cur_round_and_defend_round:
                if not isAttackRound:
                    self.makeEffect(targetList, subSkillID)

                    if subSkillConf["lastRound"] > 1:
                        buffer["lastRound"] = subSkillConf["lastRound"] - 1
                        card.bufferContainer.append(buffer)
            else:
                card.bufferContainer.append(buffer)



    # 开始一轮之前
    def bufferEffect(self,result = ConditionEnum.con_result_None):
        # ERROR_MSG("before round   is   " + str(self.id))
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
            if condition != result:
                continue
            if isAttackRound :
                if statrType == StartTypeEnmu.cur_round_and_attack_round or statrType == StartTypeEnmu.next_round_attack_round or statrType == StartTypeEnmu.cur_round:
                    self.makeEffect(targetList, subSkillID)
                    self.bufferAfterUse(i)
            else:
                if statrType == StartTypeEnmu.cur_round_and_defend_round or statrType == StartTypeEnmu.next_round_defend_round or statrType == StartTypeEnmu.cur_round:
                    self.makeEffect(targetList, subSkillID)
                    self.bufferAfterUse(i)


    # 使用完之后减少持续轮数
    def bufferAfterUse(self, i):
        # 倒序删除
        buffer = self.bufferContainer[i]
        lastRound = buffer["lastRound"]
        # 1、处理轮数
        if lastRound -1 <= 0:
            self.bufferContainer.pop(i)
        else:
            buffer["lastRound"] = lastRound -1


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

