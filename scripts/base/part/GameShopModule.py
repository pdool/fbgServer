# -*- coding: utf-8 -*-
import random

import gameShopConfig
from KBEDebug import *
from ErrorCode import GameShopModuleError
import guildShopConfig
__author__ = 'yanghao'

Diamond_type = 0
Euro_type = 1
BlackMoney_type = 2
GuildDonate_type = 3

class GameShopModule:
    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        if len(self.guildShopItemList) == 0:
            self.updateGuildShop()
            return
        self.client.onGetGuildShop(self.guildShopItemList)



        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    def onClientShopping(self, shopItemID, num):
        if len(str(shopItemID)) == 6:
            config = guildShopConfig.guildShopConfig[self.guildShopLevel * 10 + 1]
            maxTeam = config["maxTeam"]
            moneyType = GuildDonate_type
            isFind = False
            for i in range(1, maxTeam + 1):
                if isFind is True:
                    break
                config = guildShopConfig.guildShopConfig[self.guildShopLevel * 10 + i]
                priceInfo = config["price"]
                for itemID, Num in priceInfo.items():
                    if itemID == shopItemID:
                        needMoney = Num * num
                        isFind = True
                        break
        else:
            config = gameShopConfig.gameShopConfig[shopItemID]
            moneyType = config["moneyType"]
            needMoney = config["price"] * num * (config["disCount"] / 100)

        if self.delMoneyByType(moneyType, int(needMoney)) is False:
            return
        shopItem = None
        if moneyType == GuildDonate_type:
            for Item in self.guildShopItemList:
                if Item["itemID"] == shopItemID:
                    Item["limitTimes"] = Item["limitTimes"] - num
                    break
        else:
            for Item in self.gameShopItemList:
                if Item["itemID"] == shopItemID:
                    shopItem = Item
                    if config["limitTimes"] != 0:
                        Item["limitTimes"] = Item["limitTimes"] - num
                        break
            if shopItem is None:
                iteminfo = {}
                iteminfo["itemID"] = shopItemID
                if config["limitTimes"] != 0:
                    iteminfo["limitTimes"] = config["limitTimes"] - num
                else:
                    iteminfo["limitTimes"] = config["limitTimes"]
                self.gameShopItemList.append(iteminfo)

        self.client.onGetShopSucess(shopItemID)
        if moneyType == GuildDonate_type:
            self.putItemInBag(int(str(shopItemID)), num)
            return
        self.putItemInBag(int(str(shopItemID)[:6]), num)


    def onClientGetShopItemInfo(self):
        self.client.onGetShopItemInfo(self.gameShopItemList)


        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------

    def updateGuildShop(self):
        config = guildShopConfig.guildShopConfig[self.guildShopLevel * 10 + 1]

        maxTeam = config["maxTeam"]
        for i in range(1, maxTeam + 1):
            config = guildShopConfig.guildShopConfig[self.guildShopLevel * 10 + i]

            count = random.randint(0, len(config["shop"]) - 1)
            shopInfo = config["shop"]
            index = 0
            shopItem = {}
            for itemId, num in shopInfo.items():
                if index == count:
                    shopItem["itemID"] = itemId
                    shopItem["limitTimes"] = num
                    priceInfo = config["price"]
                    for itemID, Num in priceInfo.items():
                        if itemID == itemId:
                            shopItem["price"] = Num
                    self.guildShopItemList.append(shopItem)
                    break
                index = index + 1
        self.client.onGetGuildShop(self.guildShopItemList)


    def delMoneyByType(self, type, money):
        if type == Diamond_type:
            if  self.diamond < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Diamod_not_enough)
                return False
            self.diamond = self.diamond - money
        elif type == Euro_type:
            if self.euro < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Euro_not_enough)
                return False
            self.useEuro(money)
        elif type == BlackMoney_type:
            if self.blackMoney < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Black_not_enough)
                return False
            self.blackMoney = self.blackMoney - money
        elif type == GuildDonate_type:
            if self.guildDonate < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Guild_not_enough)
                return False
            self.guildDonate = self.guildDonate - money
        return True
