# -*- coding: utf-8 -*-
import TimerDefine
import util
import KBEngine
from KBEDebug import *
import random
import MentalityUpMax
from ErrorCode import CardMgrModuleError
from cardsConfig import cardsConfig
import shopConfig

__author__ = 'yanghao'

"""
意识模块
"""


class MentalityModule:
    propDict = ['shoot', 'passBall', 'reel', 'defend', 'trick', 'steal', 'controll', 'keep']

    def __init__(self):
        self.addPropertyMentality = []
        pass

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    # 请求提升意识一次
    def onClientUpMentality(self, cardId, materialtype):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardId)
        MentalityConfig = MentalityUpMax.MentalityUP[cardsConfig[card.configID]["initStar"]]
        itemCount = self.getItemNumByItemID(MentalityConfig["materialID"][materialtype])
        if itemCount < 4:
            self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
            return
        count = random.randint(1, 3)
        self.addPropertyMentality = []
        for i in range(count):
            Property = {}
            Property["name"] = random.choice(self.propDict)
            number = self.ComputeAdd(cardId, Property["name"], materialtype)
            MentalityConfig = MentalityUpMax.MentalityUP[cardsConfig[card.configID]["initStar"]]
            maxValue = MentalityConfig[Property["name"]]
            Name = Property["name"] + "M"
            if number == 0:
                Property["number"] = 1
            else:
                Property["number"] = number
            objectValue = self.GetObjectValue(cardId, Name)
            if  objectValue < maxValue and objectValue +  Property["number"] > maxValue:
                Property["number"] = maxValue - objectValue
            elif objectValue >= maxValue:
                continue
            self.addPropertyMentality.append(Property)
        itemID = MentalityConfig["materialID"][materialtype]

        self.decItem(itemID, 4)
        self.client.onMentalityUP(self.addPropertyMentality)


    # 确认提升意识属性
    def UpDateMentalityInfo(self, cardId):
        for item in self.addPropertyMentality:
            self.UpdateMainInfo(cardId, item["name"], item["number"])
        if cardId not in self.cardIDList:
            return
        card = KBEngine.entities.get(cardId)
        self.client.onBallerCallBack(CardMgrModuleError.Mentality_is_sucess)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))

    # 客户端选择属性提示
    def ChooseUpMentalityInfo(self, cardId, propertyList):
        for i in range(len(propertyList["values"])):
            index = propertyList["values"][i]["index"]
            for item in self.addPropertyMentality:
                if str(index) in item["name"]:
                    self.UpdateMainInfo(cardId, item["name"][1:], item["number"])
        if cardId not in self.cardIDList:
             return
        card = KBEngine.entities.get(cardId)
        self.client.onBallerCallBack(CardMgrModuleError.Mentality_is_sucess)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))

    # 提升意识十次
    def onClientUpTenMentality(self, cardId, materialtype):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardId)
        MentalityConfig = MentalityUpMax.MentalityUP[cardsConfig[card.configID]["initStar"]]
        itemCount = self.getItemNumByItemID(MentalityConfig["materialID"][materialtype])
        if itemCount / 40 < 1:
            self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
            return
        # TODO: 先扣东西后加属性L86   检查数量 getItemNumByItemID()
        self.addPropertyMentality = []
        for i in range(10):
            count = random.randint(1, 3)
            for j in range(count):
                Property = {}
                Property["name"] = str(i) + random.choice(self.propDict)
                Name = Property["name"][1:]
                number = self.ComputeAdd(cardId, Name, materialtype)
                MentalityConfig = MentalityUpMax.MentalityUP[cardsConfig[card.configID]["initStar"]]
                maxValue = MentalityConfig[Name]
                if number == 0:
                    Property["number"] = 1
                else:
                    Property["number"] = number
                objectValue = self.GetObjectValue(cardId, Name)
                if objectValue < maxValue and objectValue + Property["number"] > maxValue:
                    Property["number"] = maxValue - objectValue
                elif objectValue >= maxValue:
                    continue
                self.addPropertyMentality.append(Property)

        itemID = MentalityConfig["materialID"][materialtype]

        self.decItem(itemID, 40)
        self.client.onMentalityTenUP(self.addPropertyMentality)

        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------

    # 随机属性增加值
    def ComputeAdd(self, cardId, property, material):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardId)
        MentalityConfig = MentalityUpMax.MentalityUP[cardsConfig[card.configID]["initStar"]]
        maxValue = MentalityConfig[property]
        Name = property + "M"
        count = 0
        objectValue = self.GetObjectValue(cardId, Name)
        if material == 0:
            if objectValue >= 0 and objectValue < 0.2 * maxValue:
                count = self.UseFormula(0.001, 0.002, maxValue)
            elif objectValue >= 0.2 * maxValue and objectValue < 0.4 * maxValue:
                count = self.UseFormula(-0.0015, 0.0045, maxValue)
            elif objectValue >= 0.4 * maxValue and objectValue < 0.6 * maxValue:
                count = self.UseFormula(-0.003, 0.006, maxValue)
            elif objectValue >= 0.4 * maxValue and objectValue < 0.6 * maxValue:
                count = self.UseFormula(-0.005, 0.008, maxValue)
            elif objectValue >= 0.6 * maxValue and objectValue < maxValue:
                count = self.UseFormula(-0.007, 0.01, maxValue)
        else:
            if objectValue >= 0 and objectValue < 0.2 * maxValue:
                count = self.UseFormula(0.001, 0.005, maxValue)
            elif objectValue >= 0.2 * maxValue and objectValue < 0.4 * maxValue:
                count = self.UseFormula(-0.001, 0.007, maxValue)
            elif objectValue >= 0.4 * maxValue and objectValue < 0.6 * maxValue:
                count = self.UseFormula(-0.0025, 0.0085, maxValue)
            elif objectValue >= 0.4 * maxValue and objectValue < 0.6 * maxValue:
                count = self.UseFormula(-0.004, 0.01, maxValue)
            elif objectValue >= 0.6 * maxValue and objectValue < maxValue:
                count = self.UseFormula(-0.006, 0.01, maxValue)
        return int(count)

    # 利用公式计算随机值
    def UseFormula(self, num1, num2, maxValue):
        count = num1 * maxValue + num2 * maxValue * random.random()
        return count

    # 获得属性当前值
    def GetObjectValue(self, cardId, property):
        if cardId not in self.cardIDList:
            return
        card = KBEngine.entities.get(cardId)
        return getattr(card, property)

    # 设置属性当前值
    def SetObjectValue(self, cardId, property, number):
        if cardId not in self.cardIDList:
            return
        card = KBEngine.entities.get(cardId)
        setattr(card, property, number)

        # 球员意识加成到总属性上
    def UpdateMainInfo(self, cardId, name, number):
        self.SetObjectValue(cardId, name,number + self.GetObjectValue(cardId, name))
        self.SetObjectValue(cardId, name + "M", number + self.GetObjectValue(cardId, name + "M"))
