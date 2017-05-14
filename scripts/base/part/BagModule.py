# -*- coding: utf-8 -*-
import datetime
import traceback

import TimerDefine
import util
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
        self.loadPieces()
        # 加载消耗品
        self.loadUses()

        self.addTimer(60,60,TimerDefine.Time_sync_DB)
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 客户端请求背包列表
    def onClientGetItemList(self):
        retItems = []
        for uuid in self.bagUUIDList:
            _,item = self.getItemByUUID(uuid)
            if item  is None or item["state"] == DBState.Del :
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
            ERROR_MSG("-------------------uuid is ---------" +str(uuid))
            _,item = self.getItemByUUID(uuid)
            if item != None:
                # 获得数量
                ERROR_MSG("------------UUID ----------------" + str(uuid) + "  price   " + str( itemsIndex[item["itemID"]]["price"]))
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
            self.decDiamond(uuid,num)
        elif itemType == ItemTypeEnum.Equips:
            self.decEquip(uuid,num)
        elif itemType == ItemTypeEnum.Gift:
            self.decGift(uuid,num)
        elif itemType == ItemTypeEnum.Use:
            self.decUse(uuid,num)
        elif itemType == ItemTypeEnum.Pieces:
            self.decPieces(uuid,num)
        elif itemType == ItemTypeEnum.Material:
            self.decMaterial(uuid,num)

        # if result is True:
        self.rechargeEuro(num * price)
        ERROR_MSG("------------itemID ----------------" + str(itemId) + "  price   "+ str(price))

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
        elif uuid in self.usesContainer:
            item = self.usesContainer[uuid]
            itemType = ItemTypeEnum.Use
        elif uuid in self.materialsContainer:
            item = self.materialsContainer[uuid]
            itemType = ItemTypeEnum.Material
        elif uuid in self.diamondsContainer:
            item = self.diamondsContainer[uuid]
            itemType = ItemTypeEnum.Diamond
        elif uuid in self.piecesContainer:
            item = self.piecesContainer[uuid]
            itemType = ItemTypeEnum.Pieces
        elif uuid in self.giftsContainer:
            item = self.giftsContainer[uuid]
            itemType = ItemTypeEnum.Gift

        return itemType,item

    # 加一个道具到背包，并分发到各个容器
    def putItemInBag(self,itemID,num):
        itemID = int(itemID)
        if itemID not in itemsIndex:
            return False


        itemIndex = itemsIndex[itemID]
        itemType = itemIndex["itemsType"]

        # 检查背包大小
        isTogether = itemIndex["isTogether"]

        needBagSize = 1
        if isTogether <= 0:
            needBagSize = num

        if len(self.bagUUIDList)+ needBagSize > self.bagSize:
            ERROR_MSG("putItemInBag  itemId  "+str(itemID)+"   len  " + str(len(self.bagUUIDList)) + "  needBagSize " + str(needBagSize) + "  bagSize  " + str(self.bagSize))
            return False
        ERROR_MSG(
            "putItemInBag  itemId  " + str(itemID) + "   len  " + str(len(self.bagUUIDList)) + "  needBagSize " + str(
                needBagSize) + "  bagSize  " + str(self.bagSize))
        if itemType == ItemTypeEnum.Equips:
            return self.addEquipByItemID(itemID,num)
        elif itemType == ItemTypeEnum.Use:
            return self.addUse(itemID,num)
        elif itemType == ItemTypeEnum.Material:
            return self.addMaterial(itemID,num)
        elif itemType == ItemTypeEnum.Diamond:
            return self.addDiamond(itemID,num)
        elif itemType == ItemTypeEnum.Pieces:
            return self.addPieces(itemID,num)
        elif itemType == ItemTypeEnum.Gift:
            return self.addGift(itemID,num)

    # 根据itemID获得数量
    def getItemNumByItemID(self,itemID):
        count = 0
        for uuid in self.bagUUIDList:
            _, item = self.getItemByUUID(uuid)
            if item is None:
                continue
            if item["itemID"] == int(itemID):
                count = count +  item["amount"]

        return count

    # 删除物品
    def decItem(self,itemID,num):
        itemID = int(itemID)
        itemIndex = itemsIndex[itemID]
        itemType = itemIndex["itemsType"]
        ERROR_MSG(" decItem  itemID " + str(itemID) +"     itemType   " + str(itemType) + "   num  " + str(num))

        decCount = num

        for uuid in self.bagUUIDList:
            _, item = self.getItemByUUID(uuid)
            if item is None:
                continue

            if decCount <= 0:
                break
            if item["itemID"] == itemID:
                result = False
                amount = item["amount"]
                if amount < decCount:
                    num = amount


                ERROR_MSG("  itemID   is "+ str(itemID) +"   amount  "+ str(item["amount"]))
                if itemType == ItemTypeEnum.Diamond:
                    result = self.decDiamond(uuid, num)
                elif itemType == ItemTypeEnum.Equips:
                    result = self.decEquip(uuid, num)
                elif itemType == ItemTypeEnum.Gift:
                    result = self.decGift(uuid, num)
                elif itemType == ItemTypeEnum.Use:
                    result = self.decUse(uuid, num)
                elif itemType == ItemTypeEnum.Pieces:
                    result = self.decPieces(uuid, num)
                elif itemType == ItemTypeEnum.Material:
                    result = self.decMaterial(uuid, num)

                decCount = decCount - amount

                # if result is True:
                #     ERROR_MSG("bagModule result is True")
                #     value = {}
                #     value["UUID"] = uuid
                #     value["itemID"] = itemID
                #     value["amount"] = item["amount"] - num
                #     self.client.onGetItemInfo(value)
                # else:
                #     ERROR_MSG("bagModule result is False")
                # return result
        return  False

    def noticeClientBagUpdate(self,uuid,itemId,num):
        if uuid not in self.bagUUIDList:
            if num != 0:
                self.bagUUIDList.append(uuid)
            else:
                ERROR_MSG("--------exec  Error  check now!!! -----------")
                util.printStackTrace("noticeClientBagUpdate   ")
        value = {}
        value["UUID"] = uuid
        value["itemID"] = int(itemId)
        value["amount"] =  num
        self.client.onGetItemInfo(value)

        if num <= 0:
            self.bagUUIDList.remove(uuid)

    def onTimer(self, tid, userArg):
        ERROR_MSG("ontimer" + str(userArg))
        if userArg != TimerDefine.Time_sync_DB:
            return

        self.onTimerSaveBag()

    def onTimerSaveBag(self):
        now = datetime.datetime.now()

        now.strftime('%Y-%m-%d %H:%M:%S')
        ERROR_MSG(" syn DB-=================================================" + str(now))
        self.onTimerSyncDiamondDB()
        self.onTimerSyncEquipDB()
        self.onTimerSyncGiftDB()
        self.onTimerSyncMaterialDB()
        self.onTimerSyncPieceDB()
        self.onTimerSyncUseDB()

class ItemOrderBy:
    byItemType = 1
    byQualityOrder = 2

class ItemTypeEnum:

    # 错误类型
    Wrong = 1000

    Equips = 1001
    # 消耗品
    Use = 1002
    # 宝石
    Diamond = 1003
    # 礼包
    Gift = 1004
    # 材料
    Material = 1005
    # 球员碎片
    Pieces = 1006

class DBState:
    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2



        # 装备

if __name__ == "__main__":
    print(__file__)
    pass




















