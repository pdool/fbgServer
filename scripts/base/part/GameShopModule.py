# -*- coding: utf-8 -*-
import gameShopConfig
from KBEDebug import *
from ErrorCode import GameShopModuleError

__author__ = 'yanghao'


class GameShopModule:
    def __init__(self):
        pass

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    def onClientShopping(self, shopItemID, num):
        config = gameShopConfig.gameShopConfig[shopItemID]
        moneyType = config["moneyType"]
        needMoney = config["price"] * num * (config["disCount"] / 100)
        if self.delMoneyByType(moneyType, needMoney) is False:
            return
        shopItem = None
        for Item in self.gameShopItemList:
            if Item["itemID"] == shopItemID:
                shopItem = Item
                if config["limitTimes"] != 0:
                    Item["limitTimes"] = Item["limitTimes"] - num
        if shopItem is None:
            iteminfo = {}
            iteminfo["itemID"] = shopItemID
            if config["limitTimes"] != 0:
                iteminfo["limitTimes"] = config["limitTimes"] - num
            else:
                iteminfo["limitTimes"] = config["limitTimes"]
            self.gameShopItemList.append(iteminfo)
        self.client.onShopInfoCallBack(GameShopModuleError.Shopping_sucess)
        self.putItemInBag(shopItemID, num)


    def onClientGetShopItemInfo(self):
        self.client.onGetShopItemInfo(self.gameShopItemList)


        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------

    def delMoneyByType(self, type, money):
        if type == 0 and self.diamond < money:
            self.client.onShopInfoCallBack(GameShopModuleError.Diamod_not_enough)
            return False
            self.diamond = self.diamond - money
        elif type == 1 and self.euro < money:
            self.client.onShopInfoCallBack(GameShopModuleError.Euro_not_enough)
            return False
            self.useEuro(money)
        elif type == 2 and self.blackMoney < money:
            self.client.onShopInfoCallBack(GameShopModuleError.Black_not_enough)
            return False
            self.blackMoney = self.blackMoney - money
        return True
