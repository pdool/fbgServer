# -*- coding: utf-8 -*-
import TimerDefine

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from ErrorCode import GiftModuleError
from itemsConfig import itemsIndex
"""
礼包容器
"""
class GiftContainer:

    def __init__(self):
        # 礼包容器
        self.giftsContainer = {}
    def loadGifts(self):

        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemGifts", colTupe, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("GiftModule  loadGifts")
            if result is None:
                return
            for i in range(len(result)):
                giftItem = {}
                uuid = int(result[i][0])
                giftItem[GiftItemKeys.uuid] = uuid
                giftItem[GiftItemKeys.itemID] = int(result[i][1])
                giftItem[GiftItemKeys.amount] = int(result[i][2])
                giftItem[GiftItemKeys.itemState] = DBState.NoAction

                self.giftsContainer[giftItem[GiftItemKeys.uuid]] = giftItem

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加宝石
    def addGift(self,configID,count = 1):
        # 1、是否可以合并
        togetherCount = 1
        giftConfig = itemsIndex[configID]
        if giftConfig["togetherCount"] != 0:
            togetherCount = giftConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertGifts(configID, 1)
        else:
            return self.__updateGifts(configID, count)
    # 减少宝石
    def decGift(self,uuid,count):
        if uuid not in self.giftsContainer:
            self.client.onGiftError(GiftModuleError.Gift_not_exist)
            return
        ERROR_MSG("-----------decGift---------uuid-----------" + str(uuid))
        curCount = self.giftsContainer[uuid]["amount"]
        itemID = self.giftsContainer[uuid]["itemID"]

        if curCount < count:
            self.client.onGiftError(GiftModuleError.Gift_not_enough)
            return

        if curCount > count:
            self.giftsContainer[uuid]["amount"] = curCount - count
            if self.giftsContainer[uuid]["state"] != DBState.Insert:
                self.giftsContainer[uuid]["state"] = DBState.Update
            self.noticeClientBagUpdate(uuid, self.giftsContainer[uuid]["itemID"], curCount - count)
            return True

        elif curCount == count:
            oldState =  self.giftsContainer[uuid]["state"]
            if oldState == DBState.Insert:
                del self.giftsContainer[uuid]
            elif oldState == DBState.Update or oldState == DBState.NoAction:
                self.giftsContainer[uuid]["state"] = DBState.Del
            self.noticeClientBagUpdate(uuid, itemID, 0)




    def __insertGifts(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count
        rowValueMap["state"] = DBState.Insert
        self.giftsContainer[rowValueMap["UUID"]] = rowValueMap
        self.noticeClientBagUpdate(rowValueMap["UUID"],configID,count)

        return True

    def __updateGifts(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.giftsContainer.values():
            if item["itemID"] != configID or item["state"] == DBState.Del:
                continue
            isFind = True
            curCount = item["amount"]

            item["amount"] = curCount + addCount

            if item["state"] != DBState.Insert:
                item["state"] = DBState.Update
            self.noticeClientBagUpdate(item["UUID"], configID, curCount + addCount)
            break
        if isFind == True:
            return True
        return self.__insertGifts(configID, addCount)

    # 存储数据库
    def onTimerSyncGiftDB(self):
        delKeys = []
        for item in self.giftsContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertGiftDB(item)
            # 更新
            elif state == DBState.Update:
                self.updateGiftDB(item)
            # 删除
            elif state == DBState.Del:
                self.delGiftDB(item)
                delKeys.append(item["UUID"])

        for key in delKeys:
            del self.giftsContainer[key]

    def insertGiftDB(self,item):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = item["UUID"]
        rowValueMap["itemID"] = item["itemID"]
        rowValueMap["amount"] = item["amount"]

        item["state"] = DBState.NoAction

        sql = util.getInsertSql("tbl_ItemGifts", rowValueMap)

        KBEngine.executeRawDatabaseCommand(sql)

        pass
    def updateGiftDB(self,item):
        setMap = {"amount": item["amount"]}
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
        item["state"] = DBState.NoAction
        sql = util.getUpdateSql("tbl_ItemGifts", setMap, filterMap)

        KBEngine.executeRawDatabaseCommand(sql)

    def delGiftDB(self,item):
        filterMap = {"roleID": self.databaseID, "UUID":  item["UUID"]}
        sql = util.getDelSql("tbl_ItemGifts", filterMap)
        KBEngine.executeRawDatabaseCommand(sql)

class GiftItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemState = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
