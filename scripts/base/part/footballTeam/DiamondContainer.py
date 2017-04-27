# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from ErrorCode import DiamondModuleError
from itemsConfig import itemsIndex
"""
宝石容器
"""
class DiamondContainer:

    def __init__(self):
        # 宝石容器
        self.diamondsContainer = {}
    def loadDiamonds(self):

        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemDiamonds", colTupe, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("DiamondModule  loadDiamonds")
            if result is None:
                return
            for i in range(len(result)):
                diamondItem = {}
                uuid = int(result[i][0])
                diamondItem[DiamondItemKeys.uuid] = uuid
                diamondItem[DiamondItemKeys.itemID] = int(result[i][1])
                diamondItem[DiamondItemKeys.amount] = int(result[i][2])
                diamondItem[DiamondItemKeys.itemState] = DBState.NoAction

                self.diamondsContainer[diamondItem[DiamondItemKeys.uuid]] = diamondItem

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加宝石
    def addDiamond(self,configID,count):
        # 1、是否可以合并
        togetherCount = 1
        diamondConfig = itemsIndex[configID]
        if diamondConfig["togetherCount"] != 0:
            togetherCount = diamondConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertDiamonds(configID, 1)
            return True
        else:
            return self.__updateDiamonds(configID, count)
    # 减少宝石
    def decDiamond(self,uuid,count):
        if uuid not in self.diamondsContainer:
            self.client.onDiamondError(DiamondModuleError.Diamond_not_exist)
            return False
        ERROR_MSG("-----------decDiamond---------uuid-----------" + str(uuid))
        curCount = self.diamondsContainer[uuid]["amount"]
        itemID = self.diamondsContainer[uuid]["itemID"]

        if curCount < count:
            self.client.onDiamondError(DiamondModuleError.Diamond_not_enough)
            return False

        if curCount > count:
            self.diamondsContainer[uuid]["amount"] = curCount - count
            if self.diamondsContainer[uuid]["state"] != DBState.Insert:
                self.diamondsContainer[uuid]["state"] = DBState.Update

            self.noticeClientBagUpdate(uuid, self.diamondsContainer[uuid]["itemID"], curCount - count)
            return True

        elif curCount == count:
            oldState =  self.diamondsContainer[uuid]["state"]
            if oldState == DBState.Insert:
                del self.diamondsContainer[uuid]
            elif oldState == DBState.Update or oldState == DBState.NoAction:
                self.diamondsContainer[uuid]["state"] = DBState.Del
            self.noticeClientBagUpdate(uuid, itemID, 0)
            return True



    def __insertDiamonds(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count
        rowValueMap["state"] = DBState.Insert
        self.diamondsContainer[rowValueMap["UUID"]] = rowValueMap
        self.noticeClientBagUpdate(rowValueMap["UUID"],configID,count)

        return True

    def __updateDiamonds(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.diamondsContainer.values():
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
        return self.__insertDiamonds(configID, addCount)

    # 存储数据库
    def onTimerSyncDiamondDB(self):

        delKeys = []
        for item in self.diamondsContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertDiamondDB(item)
            # 更新
            elif state == DBState.Update:
                self.updateDiamondDB(item)
            # 删除
            elif state == DBState.Del:
                self.deDiamondDB(item)
                delKeys.append(item["UUID"])

        for key in delKeys:
            del self.diamondsContainer[key]

    def insertDiamondDB(self,item):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = item["UUID"]
        rowValueMap["itemID"] = item["itemID"]
        rowValueMap["amount"] = item["amount"]

        item["state"] = DBState.NoAction

        sql = util.getInsertSql("tbl_ItemDiamonds", rowValueMap)

        KBEngine.executeRawDatabaseCommand(sql)

        pass
    def updateDiamondDB(self,item):
        setMap = {"amount": item["amount"]}
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}

        item["state"] = DBState.NoAction

        sql = util.getUpdateSql("tbl_ItemDiamonds", setMap, filterMap)
        KBEngine.executeRawDatabaseCommand(sql)

    def delDiamondDB(self,item):
        filterMap = {"roleID": self.databaseID, "UUID":  item["UUID"]}
        sql = util.getDelSql("tbl_ItemDiamonds", filterMap)


        KBEngine.executeRawDatabaseCommand(sql)

class DiamondItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemState = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
