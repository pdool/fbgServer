# -*- coding: utf-8 -*-
from itemsConfig import itemsIndex

__author__ = 'chongxin'
__createTime__  = '2016年12月26日'
"""
背包模块
"""
class BagModule:


    def onEntitiesEnabled(self):
        # 加载宝石
        self.loadDiamonds()
        # 加载装备
        self.loadEquips()
        # 加载礼包
        self.loadGifts()
        # 加载材料
        self.loadMaterial()
        # 加载碎片
        self.loadPiecesItem()
        # 加载消耗品
        self.loadUse()
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 客户端请求背包列表
    def onClientGetItemList(self):

        retItems = []
        for uuid in self.bagUUIDList:
            item = self.getItemByUUID(uuid)
            if item  is None:
                continue
            value = {}
            value["UUID"] = uuid
            value["itemID"] = item["itemID"]
            value["amount"] = item["amount"]
            retItems.append(value)

        self.client.onGetItemList(retItems)



    def onClientSellBatch(self,uuidList):

        for uuid in uuidList:
            # 获得装备
            item = self.getItemByUUID(uuid)
            if item != None:
                # 获得数量
                amount = item["amount"]
                self.onClientSellOne(uuid,amount)



    def onClientSellOne(self,uuid,num):

        item = self.getItemByUUID(uuid)

        if item is None:
            return
        ammount = item["amount"]

        if num > ammount:
            return

        # 获得装备ID
        itemId = item["itemID"]
        # 获得单价
        price = itemsIndex[itemId]["price"]

        sellMoney = self.gold + num * price

        itemType =  item["itemType"]
        result = False
        if itemType == ItemTypeEnum.Diamond:
            result = self.decDiamond(self,uuid,num)
        elif itemType == ItemTypeEnum.Equips:
            result = self.decEquips(self,uuid,num)
        elif itemType == ItemTypeEnum.Gift:
            result = self.decGift(self,uuid,num)
        elif itemType == ItemTypeEnum.Use:
            result = self.decUse(self,uuid,num)
        elif itemType == ItemTypeEnum.Pieces:
            result = self.decPieces(self,uuid,num)
        elif itemType == ItemTypeEnum.Material:
            result = self.decMaterial(self,uuid,num)

        if result is True:
            self.gold = sellMoney


    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def getItemByUUID(self,uuid):
        item = None
        if uuid in self.equipsContainer:
            item = self.equipsContainer[uuid]
        elif uuid in self.useContainer:
            item = self.useContainer[uuid]
        elif uuid in self.materialContainer:
            item = self.materialContainer[uuid]
        elif uuid in self.diamondsContainer:
            item = self.diamondsContainer[uuid]
        elif uuid in self.piecesContainer:
            item = self.piecesContainer[uuid]
        elif uuid in self.giftContainer:
            item = self.giftContainer[uuid]

        return item

    # 加一个道具到背包，并分发到各个容器
    def putItemInBag(self,itemID,num):
        if itemID not in itemsIndex:
            return

        itemIndex = itemsIndex[itemID]
        itemType = itemIndex["itemsType"]

        if itemType == ItemTypeEnum.Equips:
            self.addEquip(itemID,num)
        elif itemType == ItemTypeEnum.Use:
            self.addUse(itemID,num)
        elif itemType == ItemTypeEnum.Material:
            self.addMaterial(itemID,num)
        elif itemType == ItemTypeEnum.Diamond:
            self.addDiamond(itemID,num)
        elif itemType == ItemTypeEnum.Pieces:
            self.addPieces(itemID,num)
        elif itemType == ItemTypeEnum.Gift:
            self.addGift(itemID,num)


class ItemOrderBy:
    byItemType = 1
    byQualityOrder = 2

class ItemTypeEnum:
    Equips = 1001
    # 消耗品
    Use = 1002
    # 材料
    Material = 1003
    # 宝石
    Diamond = 1004
    # 球员碎片
    Pieces = 1005
    # 礼包
    Gift = 1006









    # 装备

if __name__ == "__main__":
    print(__file__)
    pass




















