# -*- coding: utf-8 -*-
import TimerDefine
import util
from ErrorCode import SkillModuleError, CardMgrModuleError
from KBEDebug import *
import coachConfig
import  cardsConfig
import skillLevelConfig
import CommonConfig
__author__ = 'yanghao'


# 技能模块
class SkillModule:
    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        if len(self.coachList) == 0:
            for i in  range (1,6):
                item={}
                item["id"] = i
                item["limitTime"] = coachConfig.coachConfig[i]["limitTime"]
                item["useTime"] = 0
                item["periodTime"] = 0
                item["color"] = coachConfig.coachConfig[i]["color"]
                item["isLock"] = coachConfig.coachConfig[i]["isLock"]
                item["cost"] = ""
                for itemID,Num in coachConfig.coachConfig[i]["cost"].items():
                    item["cost"] = item["cost"] + str(itemID)  +":"+str(Num)+","
                self.coachList.append(item)
                self.coachLastTime = util.getCurrentTime()

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def onClientGetCoachList(self):
        period = util.getCurrentTime() - self.coachLastTime
        self.coachLastTime = util.getCurrentTime()
        for item in self.coachList:
            if item["isLock"] == 0:
                continue
            if item["useTime"] < period:
                item["useTime"] = 0
            else:
                item["useTime"] = item["useTime"] - period
        self.client.onGetCoachList(self.coachList)

    def onClientSkillLevelUp(self,skillID,skillIndex,cardId):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        skillName = ""
        card = KBEngine.entities.get(cardId)
        if card.isSelf == 1 and skillIndex == 1:
            if skillID == card.skill11 // 100:
                skillName = "skill11"
            elif skillID == card.skill12 // 100:
                skillName = "skill12"
            elif skillID == card.skill13 // 100:
                skillName = "skill13"
        else:
            skillName = self.GetSkillByIndex(skillID,cardId)
        if skillName =="":
            ERROR_MSG("skillName is empty")
            return
        currentLevel = self.GetObjectValue(cardId, skillName)
        currentLevel = currentLevel - currentLevel//100 * 100
        if currentLevel >= len(skillLevelConfig.SkillUpTimeConfig):
            self.client.onSkillError(SkillModuleError.skill_is_max)
            return
        levelConfig = skillLevelConfig.SkillUpTimeConfig[int(currentLevel)]
        coachID = 0
        findItem = None
        for item in self.coachList:
            coachID = coachID + 1
            period = util.getCurrentTime() -  item["periodTime"]
            item["periodTime"] = util.getCurrentTime()
            if item["useTime"] < period:
                item["useTime"] = 0
            else:
                item["useTime"] = item["useTime"] - period

            if  item["useTime"]  < item["limitTime"] and item["isLock"] == 1:
                findItem = item
                break
        if findItem == None:
            self.client.onSkillError(SkillModuleError.coach_time_not_enough)
            return
        findItem["useTime"] = findItem["useTime"] + levelConfig["upTime"] * 60
        self.SetObjectValue(cardId, skillName, skillID * 100 + (currentLevel + 1))
        if card.isSelf == 1 and skillIndex == 1:
            self.SetObjectValue(cardId, "skill1", skillID * 100 + (currentLevel + 1))
        if skillIndex > 2 :
            config = skillLevelConfig.PropSkillLevelConfig[skillID * 100 + currentLevel]
            for itemID,Num in config["addvalue"].items():
                addValue = self.GetObjectValue(cardId, itemID) + Num
                self.SetObjectValue(cardId, itemID, addValue)
        self.client.onSkillLevelUpSucess(currentLevel + 1,findItem["useTime"],coachID)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))


    def onClientUnLockCoach(self, coachID):
        config = CommonConfig.CommonConfig[coachID]
        if self.delMoneyByType(0, config["value"]) is False:
            return
        for item in self.coachList:
            if item["id"] == coachID:
                item["isLock"] = 1
        self.client.onUnLockCoach(coachID)

    def onClientLevelUpCoach(self, coachID,commonIndex):
        if commonIndex == 0:
            diamond = CommonConfig.CommonConfig[12]["value"]
        else:
            diamond = CommonConfig.CommonConfig[13]["value"]
        if self.delMoneyByType(0, int(diamond)) is False:
            return
        for item in self.coachList:
            if item["id"] == coachID:
                item["color"] = item["color"] + 1
                item["limitTime"] = item["limitTime"] + int(coachConfig.coachConfig[coachID]["addTime"][commonIndex])
                break
        self.client.onLevelUpCoachSucess(coachID,item["limitTime"])

    def onClientAddCoachTime(self, itemID, coachID):
        index = 0
        findItem = None
        for item in self.coachList:
            if item["id"] == coachID:
                period = util.getCurrentTime() - item["periodTime"]
                item["periodTime"] = util.getCurrentTime()
                if item["useTime"] < period:
                    item["useTime"] = 0
                else:
                    item["useTime"] = item["useTime"] - period
                findItem = item
                break
        for itemId, num in coachConfig.coachConfig[coachID]["cost"].items():
            if itemId == itemID:
                if self.getItemNumByItemID(itemId) < 1:
                    self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
                    return
                if index == 0:
                    if findItem["useTime"] - (int(num) * 3600) < 0:
                        findItem["useTime"] = 0
                    else:
                        findItem["useTime"] = findItem["useTime"] - (int(num) * 3600)
                elif index == 1:
                    if findItem["useTime"] - findItem["useTime"]//2 < 0:
                        findItem["useTime"] = 0
                    else:
                        findItem["useTime"] = findItem["useTime"] - findItem["useTime"]//2
                elif index == 2:
                    findItem["useTime"] = 0
                break
            index = index + 1
        self.client.onAddCoachTimeSucess(coachID,index, findItem["useTime"])
        self.decItem(itemId, 1)

    def onClientSelectSkill(self, skillID,cardID):
        if cardID not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardID)
        if card.skill11 // 100 == skillID:
            card.skill1 = card.skill11
        elif card.skill12 // 100 == skillID:
            card.skill1 = card.skill12
        else:
            card.skill1 = card.skill13
        self.client.onSelectSkillSucess(skillID,card.skill1 - card.skill1 // 100 * 100)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def GetSkillByIndex(self,skillID,cardId):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardId)
        config = cardsConfig.cardsConfig[card.configID]
        if skillID == config["skill1ID"]:
            return  "skill1"
        elif skillID == config["skill2ID"]:
            return "skill2"
        elif skillID == config["skill3ID"]:
            return "skill3"
        elif skillID == config["skill4ID"]:
            return "skill4"
        else:
            return ""