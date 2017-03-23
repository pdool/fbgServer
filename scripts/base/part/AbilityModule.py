# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *
import PowerConfig
import CardByColor
import itemsPieces
import cardsConfig
from ErrorCode import CardMgrModuleError
import shopConfig

__author__ = 'yanghao'

if __name__ == "__main__":
    pass
"""
能力模块
"""


class AbilityModule:
    def __init__(self):
        self.pieceAddExp = 0
        self.currentLevel = 0
        pass

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    def onClientUpAbilityInfo(self, cardId, property, selectList):

        ERROR_MSG("onClientUpAbilityInfo " + str(cardId) + "    " + property)
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        self.pieceAddExp = 0

        for i in range(len(selectList)):
            itemID = selectList[i]["itemID"]
            amount = selectList[i]["number"]
            # 判断碎片数量
            itemCount = self.getItemNumByItemID(itemID)
            if itemCount < amount:
                self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
                return
            # 球员ID
            materialId = itemsPieces.itemsPiecesConfig[itemID]["cardID"]
            # 碎片初始星级
            cardStar = cardsConfig.cardsConfig[materialId]["initStar"]
            # 根据星级 消耗数量计算所加经验值
            exp = CardByColor.UsePieces[cardStar]["exp"] * amount
            # 总经验 叠加
            self.pieceAddExp = self.pieceAddExp + exp
        # 获取球员该属性当前经验值
        baller = KBEngine.entities.get(cardId)
        ballerPropertyExp = getattr(baller, property)
        # 判断有没有满级
        maxExp = PowerConfig.PowerConfig[29]["exp"]
        if ballerPropertyExp >= maxExp:
            self.client.onBallerCallBack(CardMgrModuleError.Property_is_max)
            return
        allExp = ballerPropertyExp + self.pieceAddExp
        # 通过经验值判断属性当前等级
        self.currentLevel = 0
        for i in range(28):
            level = i + 1
            needExp = PowerConfig.PowerConfig[level]["exp"]
            if ballerPropertyExp < needExp:
                self.currentLevel = level
                break
            elif ballerPropertyExp == needExp:
                self.currentLevel = level + 1
                break

        setattr(baller, property, allExp)
        for i in range(len(selectList)):
            itemID = selectList[i]["itemID"]
            amount = selectList[i]["number"]
            self.decItem(itemID, amount)

        # 经验增加不足以升一级
        changeLevel = self.currentLevel
        if allExp < PowerConfig.PowerConfig[changeLevel]["exp"]:
            self.client.onBallerCallBack(CardMgrModuleError.Ability_is_sucess)
            return

        # 根据经验值重置等级 增加对应属性值
        while (changeLevel < len(PowerConfig.PowerConfig)):
            config = PowerConfig.PowerConfig[changeLevel]
            needExp = config["exp"]
            if allExp >= needExp:
                changeLevel = changeLevel + 1
                config = PowerConfig.PowerConfig[changeLevel]
                # 截取从头开始到倒数第三个字符之前
                Name = property[:-3]
                self.SetObjectValue(cardId, Name, getattr(baller, Name) + config[Name])
            else:
                self.client.onBallerCallBack(CardMgrModuleError.Ability_is_sucess)
                break






                # --------------------------------------------------------------------------------------------
                #                              工具函数调用函数
                # --------------------------------------------------------------------------------------------
