# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *
from ErrorCode import UseModuleError
from itemsConfig import itemsIndex

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'
"""
消耗品容器
"""
class UseContainer:

    def __init__(self):
        # 消耗品容器
        self.usesContainer = {}
    def loadUses(self):

        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemUses", colTupe, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("UseModule  loadUses")
            if result is None:
                return
            for i in range(len(result)):
                giftItem = {}
                uuid = int(result[i][0])
                giftItem[UseItemKeys.uuid] = uuid
                giftItem[UseItemKeys.itemID] = int(result[i][1])
                giftItem[UseItemKeys.amount] = int(result[i][2])
                giftItem[UseItemKeys.itemState] = DBState.NoAction

                self.usesContainer[giftItem[UseItemKeys.uuid]] = giftItem

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加宝石
    def addUse(self,configID,count = 1):
        # 1、是否可以合并
        togetherCount = 1
        useConfig = itemsIndex[configID]
        if useConfig["togetherCount"] != 0:
            togetherCount = useConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertUse(configID, 1)
            return True
        else:
            return self.__updateUse(configID, count)
    # 减少宝石
    def decUse(self,uuid,count):
        if uuid not in self.usesContainer:
            self.client.onUseError(UseModuleError.Use_not_exist)
            return False
        ERROR_MSG("-----------decUse---------uuid-----------" + str(uuid))
        curCount = self.usesContainer[uuid]["amount"]
        itemID = self.usesContainer[uuid]["itemID"]

        if curCount < count:
            self.client.onUseError(UseModuleError.Use_not_enough)
            return False

        if curCount > count:
            self.usesContainer[uuid]["amount"] = curCount - count
            if self.usesContainer[uuid]["state"] != DBState.Insert:
                self.usesContainer[uuid]["state"] = DBState.Update
            self.noticeClientBagUpdate(uuid, self.usesContainer[uuid]["itemID"], curCount - count)
            return True

        elif curCount == count:
            oldState =  self.usesContainer[uuid]["state"]
            if oldState == DBState.Insert:
                del self.usesContainer[uuid]
            elif oldState == DBState.Update or oldState == DBState.NoAction:
                self.usesContainer[uuid]["state"] = DBState.Del
            self.noticeClientBagUpdate(uuid, itemID, 0)

            return True




    def __insertUse(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count
        rowValueMap["state"] = DBState.Insert
        self.usesContainer[rowValueMap["UUID"]] = rowValueMap
        self.noticeClientBagUpdate(rowValueMap["UUID"],configID,count)

        return True

    def __updateUse(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.usesContainer.values():
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
        return self.__insertUse(configID, addCount)

    # 存储数据库
    def onTimerSyncUseDB(self):
        delKeys = []
        for item in self.usesContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertUseDB(item)
            # 更新
            elif state == DBState.Update:
                self.updateUseDB(item)
            # 删除
            elif state == DBState.Del:
                self.delUseDB(item)
                delKeys.append(item["UUID"])

        for key in delKeys:
            del self.usesContainer[key]

    def insertUseDB(self,item):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = item["UUID"]
        rowValueMap["itemID"] = item["itemID"]
        rowValueMap["amount"] = item["amount"]

        item["state"] = DBState.NoAction

        sql = util.getInsertSql("tbl_ItemUses", rowValueMap)

        KBEngine.executeRawDatabaseCommand(sql)

    def updateUseDB(self,item):
        setMap = {"amount": item["amount"]}
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
        item["state"] = DBState.NoAction
        sql = util.getUpdateSql("tbl_ItemUses", setMap, filterMap)

        KBEngine.executeRawDatabaseCommand(sql)

    def delUseDB(self,item):
        filterMap = {"roleID": self.databaseID, "UUID":  item["UUID"]}
        sql = util.getDelSql("tbl_ItemUses", filterMap)
        KBEngine.executeRawDatabaseCommand(sql)

class UseItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemState = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
