# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月12日'

import util
import random
from KBEDebug import *
from ErrorCode import GiftModuleError
from itemsConfig import itemsIndex
from part.BagModule import ItemTypeEnum
from itemsGift import itemsGiftConfig
from itemGiftChange import itemGiftChangeConfig
class GiftKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"

    giftType = "giftType"

    percentList = "percentList"
    percent = "percent"
    keyItemID = "keyItemID"
    percentIndex = "percentIndex"

class GiftTypeEnum:
    # 纯随机
    random = 1
    # select
    select = 2
    # 几率变化的随机礼包
    accPercent = 3


"""
礼包容器
"""
class GiftModule:

    def __init__(self):
        # 球员碎片容器
        self.giftContainer = {}
    def loadGifts(self):
        DEBUG_MSG("GiftModule  loadGifts")

        colTupe = ("sm_UUID", "sm_itemID", "sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemGifts", colTupe, filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("GiftsModule  loadGiftsItem")
            if result is None:
                return

            for i in range(len(result)):
                giftItem = {}
                giftItem[GiftKeys.uuid] = int(result[i][0])
                giftItem[GiftKeys.itemID] = int(result[i][1])
                giftItem[GiftKeys.amount] = int(result[i][2])
                giftItem[GiftKeys.itemType] = ItemTypeEnum.Gift
                self.giftContainer[giftItem[GiftKeys.uuid]] = giftItem

                if giftItem[GiftKeys.uuid] not in self.bagUUIDList:
                    self.bagUUIDList.append(giftItem[GiftKeys.uuid])

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # 增加礼包
    def addGift(self, configID, count = 1):
        # 1、是否可以合并
        togetherCount = 1
        giftConfig = itemsIndex[configID]
        if giftConfig["togetherCount"] != 0:
            togetherCount = giftConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertGift(configID, count)
        else:
            self.__updateGifts(configID, count)

    # 打开礼包
    def decGift(self, uuid, count = 1):
        if uuid not in self.giftContainer:
            self.onGiftError(GiftModuleError.Gift_not_exist)
            return

        curCount = self.giftContainer[uuid]["amount"]

        if curCount < count:
            self.onGiftError(GiftModuleError.Gift_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemGifts", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                self.giftContainer[uuid]["amount"] = curCount - count
                return

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemGifts", filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                del self.giftContainer[uuid]
                self.bagUUIDList.remove(uuid)
                self.writeToDB()

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertGift(self, configID, count=1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemGifts", rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onGiftError(GiftModuleError.Gift_db_error)
                return
            else:
                self.giftContainer[rowValueMap["UUID"]] = rowValueMap
                self.bagUUIDList.append(rowValueMap["UUID"])
                self.writeToDB()
                return

        KBEngine.executeRawDatabaseCommand(sql, cb)


    def __updateGifts(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.giftContainer.values():
            if item["itemID"] != configID:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemGifts", setMap, filterMap)

            def cb(result, rownum, error):
                self.giftContainer[item["UUID"]]["amount"] = curCount + addCount
                return True

            KBEngine.executeRawDatabaseCommand(sql, cb)

        if isFind == True:
            return
        return self.__insertGift(configID, addCount)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 打开纯随机礼包
    def onClientOpenRandomGift(self,uuid):
        # 1、检查背包里是否存在
        if uuid not in self.giftContainer or uuid not in self.bagUUIDList:
            self.client.onGiftError(GiftModuleError.Gift_not_exist)

        # 获得背包里的礼包道具
        giftItem = self.giftContainer[uuid]
        giftId = giftItem[GiftKeys.itemID]
        # 获取礼包的配置
        giftConfig = itemsGiftConfig[giftId]
        # 检查礼包类型
        giftType = giftConfig[GiftKeys.giftType]

        if giftType != GiftTypeEnum.random:
            return

        # 获取可随机的最大值

        percentList = giftConfig[GiftKeys.percentList]

        maxPercent = percentList[-1][GiftKeys.percent]

        randValue = random.randint(0, maxPercent)

        itemId = -1
        num = -1
        for item in percentList:
            if randValue <= item[GiftKeys.percent]:
                itemId = item["id"]
                num = item[GiftKeys.amount]
                break

        if itemId == -1 or num == -1:
            # 配置出错
            return
        # 删除礼包
        self.decGift(uuid)
        # 加进背包
        self.putItemInBag(itemId,num)

    # 打开自选礼包
    def onClientOpenSelectGift(self,uuid,itemID):
        if uuid not in self.giftContainer or uuid not in self.bagUUIDList:
            self.client.onGiftError(GiftModuleError.Gift_not_exist)

        # 获得背包里的礼包道具
        giftItem = self.giftContainer[uuid]
        giftId = giftItem[GiftKeys.itemID]
        # 获取礼包的配置
        giftConfig = itemsGiftConfig[giftId]
        # 检查礼包类型
        giftType = giftConfig[GiftKeys.giftType]

        if giftType != GiftTypeEnum.select:
            return

        if itemID not in giftConfig["select"]:
            # 非法的ID
            return

        num = giftConfig["select"][itemID]

        # 删除礼包
        if self.decGift(uuid) != True:
            return
        # 加进背包
        self.putItemInBag(itemID,num)



    # 打开概率变化的随机礼包
    def onClientOpenChangeGift(self, uuid):
        if uuid not in self.giftContainer or uuid not in self.bagUUIDList:
            self.client.onGiftError(GiftModuleError.Gift_not_exist)

        # 获得背包里的礼包道具
        giftItem = self.giftContainer[uuid]
        giftId = giftItem[GiftKeys.itemID]
        # 获取礼包的配置
        giftConfig = itemsGiftConfig[int(giftId)]
        # 检查礼包类型
        giftType = giftConfig[GiftKeys.giftType]

        if giftType != GiftTypeEnum.accPercent:
            return
        # 是否曾经开过这种礼包
        findItem  = None
        for item in self.openGiftPercentList:
            if giftId == item["giftId"]:
                findItem = item
                break

        keyStr = None

        if findItem != None:

            keyStr = str(giftId) + "-" + str(findItem[GiftKeys.percentIndex])
        else:
            keyStr = str(giftId) + "-" + str(0)

        # 获取可随机的最大值

        percentList = itemGiftChangeConfig[keyStr][GiftKeys.percentList]

        maxPercent = percentList[-1][GiftKeys.percent]

        randValue = random.randint(0, maxPercent)

        itemId = -1
        num = -1
        for item in percentList:
            if randValue <= item[GiftKeys.percent]:
                itemId = item["id"]
                num = item[GiftKeys.amount]
                break

        if itemId == -1 or num == -1:
            # 配置出错
            return
        print(itemId)
        print(num)
        # # 删除礼包
        self.decGift(uuid)
        # 加进背包
        self.putItemInBag(itemId, num)


        # 如果随机到的是关键道具，切换到下一个概率

        if int(itemId) == itemGiftChangeConfig[keyStr][GiftKeys.keyItemID]:

            if findItem != None:
                nextIndex = findItem[GiftKeys.percentIndex] + 1
            else:
                nextIndex = 1
            keyStr =  str(giftId) + "-" +  str(nextIndex)

            if keyStr in itemGiftChangeConfig:

                print("-------next----------" + keyStr)
                if findItem == None:
                    item = dict(giftId= giftId,percentIndex = nextIndex )
                    self.openGiftPercentList.append(item)
                else:
                    findItem[GiftKeys.percentIndex] = nextIndex

