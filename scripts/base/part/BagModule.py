# -*- coding: utf-8 -*-
from BagConfig import BagConfig
from itemsConfig import itemsIndex
from KBEDebug import *
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
            _,item = self.getItemByUUID(uuid)
            if item  is None:
                continue
            value = {}
            value["UUID"] = uuid
            value["itemID"] = item["itemID"]
            value["amount"] = item["amount"]
            retItems.append(value)

        ERROR_MSG("onClientGetItemList")
        self.client.onGetItemList(retItems)


    # 批量出售
    def onClientSellBatch(self,uuidList):

        for uuid in uuidList:
            # 获得装备
            _,item = self.getItemByUUID(uuid)
            if item != None:
                # 获得数量
                amount = item["amount"]
                self.onClientSellOne(uuid,amount)


    # 出售一个
    def onClientSellOne(self,uuid,num):

        itemType,item = self.getItemByUUID(uuid)

        if item is None:
            return
        ammount = item["amount"]

        if num > ammount:
            return

        # 获得装备ID
        itemId = item["itemID"]
        # 获得单价
        price = itemsIndex[itemId]["price"]

        sellMoney = self.euro + num * price

        result = False
        if itemType == ItemTypeEnum.Diamond:
            result = self.decDiamond(uuid,num)
        elif itemType == ItemTypeEnum.Equips:
            result = self.decEquip(uuid,num)
        elif itemType == ItemTypeEnum.Gift:
            result = self.decGift(uuid,num)
        elif itemType == ItemTypeEnum.Use:
            result = self.decUse(uuid,num)
        elif itemType == ItemTypeEnum.Pieces:
            result = self.decPieces(uuid,num)
        elif itemType == ItemTypeEnum.Material:
            result = self.decMaterial(uuid,num)

        if result is True:
            self.euro = sellMoney

    # 扩容
    def onClientBuyBagSize(self,count):
        needDiamond = count * BagConfig[1]["bagPrice"]

        if  self.diamond >= needDiamond:
            self.diamond = self.diamond - needDiamond
            self.bagSize = self.bagSize + count






    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def getItemByUUID(self,uuid):
        itemType = ItemTypeEnum.Wrong
        item = None

        if uuid not in self.bagUUIDList:
            return itemType,item

        if uuid in self.equipsContainer:
            item = self.equipsContainer[uuid]
            itemType = ItemTypeEnum.Equips
        elif uuid in self.useContainer:
            item = self.useContainer[uuid]
            itemType = ItemTypeEnum.Use
        elif uuid in self.materialContainer:
            item = self.materialContainer[uuid]
            itemType = ItemTypeEnum.Material
        elif uuid in self.diamondsContainer:
            item = self.diamondsContainer[uuid]
            itemType = ItemTypeEnum.Diamond
        elif uuid in self.piecesContainer:
            item = self.piecesContainer[uuid]
            itemType = ItemTypeEnum.Pieces
        elif uuid in self.giftContainer:
            item = self.giftContainer[uuid]
            itemType = ItemTypeEnum.Gift

        return itemType,item

    # 加一个道具到背包，并分发到各个容器
    def putItemInBag(self,itemID,num):
        if itemID not in itemsIndex:
            return

        itemIndex = itemsIndex[itemID]
        itemType = itemIndex["itemsType"]

        if itemType == ItemTypeEnum.Equips:
            self.addEquipByItemID(itemID,num)
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

    # 根据id获得数量
    def getItemNumByItemID(self,itemID):

        for uuid in self.bagUUIDList:
            _, item = self.getItemByUUID(uuid)
            if item is None:
                continue
            DEBUG_MSG("                   " + str(item["itemID"]) +"   " +str(type(item["itemID"])))
            if item["itemID"] == itemID:
                return item["amount"]
        return 0

    # 删除物品
    def decItem(self,itemID,num):
        for uuid in self.bagUUIDList:
            itemType, item = self.getItemByUUID(uuid)
            if item is None:
                return False

            result = False
            if itemType == ItemTypeEnum.Diamond:
                result = self.decDiamond(uuid,num)
            elif itemType == ItemTypeEnum.Equips:
                result = self.decEquip(uuid,num)
            elif itemType == ItemTypeEnum.Gift:
                result = self.decGift(uuid,num)
            elif itemType == ItemTypeEnum.Use:
                result = self.decUse(uuid,num)
            elif itemType == ItemTypeEnum.Pieces:
                result = self.decPieces(uuid,num)
            elif itemType == ItemTypeEnum.Material:
                result = self.decMaterial(uuid,num)

            return  result

        return False



class ItemOrderBy:
    byItemType = 1
    byQualityOrder = 2

class ItemTypeEnum:

    # 错误类型
    Wrong = 1000

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




















