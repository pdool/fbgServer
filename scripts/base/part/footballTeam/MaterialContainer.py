# -*- coding: utf-8 -*-

import util
from KBEDebug import *
from ErrorCode import MaterialModuleError
from itemsConfig import itemsIndex
import TimerDefine

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'
"""
材料容器
"""
class MaterialContainer:

    def __init__(self):
        # 材料容器
        self.materialsContainer = {}
    def loadMaterial(self):

        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemMaterial", colTupe, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("MaterialModule  loadMaterial")
            if result is None:
                ERROR_MSG("loadMaterial      " + error)
            for i in range(len(result)):
                item = {}
                uuid = int(result[i][0])
                item[MaterialItemKeys.uuid] = uuid
                item[MaterialItemKeys.itemID] = int(result[i][1])
                item[MaterialItemKeys.amount] = int(result[i][2])
                item[MaterialItemKeys.itemState] = DBState.NoAction

                self.materialsContainer[item[MaterialItemKeys.uuid]] = item

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加材料
    def addMaterial(self,configID,count = 1):
        # 1、是否可以合并
        togetherCount = 1
        materialConfig = itemsIndex[configID]
        if materialConfig["togetherCount"] != 0:
            togetherCount = materialConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertMaterial(configID, 1)
            return True
        else:
            return self.__updateMaterial(configID, count)
    # 减少宝石
    def decMaterial(self,uuid,count):
        if uuid not in self.materialsContainer:
            self.client.onMaterialError(MaterialModuleError.Use_not_exist)
            return False
        ERROR_MSG(" -----------decMaterial---------uuid-----------" + str(uuid))
        curCount = self.materialsContainer[uuid]["amount"]
        itemID = self.materialsContainer[uuid]["itemID"]

        if curCount < count:
            self.client.onMaterialError(MaterialModuleError.Use_not_enough)
            return False

        if curCount > count:
            self.materialsContainer[uuid]["amount"] = curCount - count
            if self.materialsContainer[uuid]["state"] != DBState.Insert:
                self.materialsContainer[uuid]["state"] = DBState.Update
            self.noticeClientBagUpdate(uuid, self.materialsContainer[uuid]["itemID"], curCount - count)
            return  True

        elif curCount == count:
            oldState =  self.materialsContainer[uuid]["state"]
            if oldState == DBState.Insert:
                del self.materialsContainer[uuid]
            elif oldState == DBState.Update or oldState == DBState.NoAction:
                self.materialsContainer[uuid]["state"] = DBState.Del
                self.materialsContainer[uuid]["amount"] = 0
            self.noticeClientBagUpdate(uuid, itemID, 0)
            return True




    def __insertMaterial(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count
        rowValueMap["state"] = DBState.Insert
        self.materialsContainer[rowValueMap["UUID"]] = rowValueMap
        self.noticeClientBagUpdate(rowValueMap["UUID"],configID,count)

        return True

    def __updateMaterial(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.materialsContainer.values():
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
        return self.__insertMaterial(configID, addCount)

    # 存储数据库
    def onTimerSyncMaterialDB(self):
        delKeys = []
        for item in self.materialsContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertMaterialDB(item)
            # 更新
            elif state == DBState.Update:
                self.updateMaterialDB(item)
            # 删除
            elif state == DBState.Del:
                self.delMaterialDB(item)
                delKeys.append(item["UUID"])

        for key in delKeys:
            del self.materialsContainer[key]

    def insertMaterialDB(self,item):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = item["UUID"]
        rowValueMap["itemID"] = item["itemID"]
        rowValueMap["amount"] = item["amount"]

        item["state"] = DBState.NoAction

        sql = util.getInsertSql("tbl_ItemMaterial", rowValueMap)

        KBEngine.executeRawDatabaseCommand(sql,None,self.id)

        pass
    def updateMaterialDB(self,item):
        setMap = {"amount": item["amount"]}
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
        item["state"] = DBState.NoAction
        sql = util.getUpdateSql("tbl_ItemMaterial", setMap, filterMap)

        KBEngine.executeRawDatabaseCommand(sql,None,self.id)

    def delMaterialDB(self,item):
        filterMap = {"roleID": self.databaseID, "UUID":  item["UUID"]}
        sql = util.getDelSql("tbl_ItemMaterial", filterMap)
        KBEngine.executeRawDatabaseCommand(sql,None,self.id)

class MaterialItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemState = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
