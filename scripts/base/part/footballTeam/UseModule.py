# -*- coding: utf-8 -*-
from random import Random

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from part.BagModule import ItemTypeEnum
from itemsConfig import itemsIndex
from ErrorCode import UseModuleError
from itemsUse import itemsUseConfig

"""
消耗品容器
"""
class UseModule:

    def __init__(self):
        # 消耗品容器
        self.useContainer = {}
    def loadUse(self):
        colTupe= ("sm_UUID","sm_itemID","sm_amount")
        filterMap = {"sm_roleID":self.databaseID}
        sql = util.getSelectSql("tbl_ItemUses",colTupe,filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("UseModule  loadUseItem")
            if error is not None:
                ERROR_MSG("UseModule      " + error)
                return
            if result is None:
                return
            for i in range(len(result)):
                useItem = {}
                useItem[UseItemKeys.uuid] = int(result[i][0])
                useItem[UseItemKeys.itemID] = int(result[i][1])
                useItem[UseItemKeys.amount] = int(result[i][2])
                useItem[UseItemKeys.itemType] = ItemTypeEnum.Use
                self.useContainer[ useItem[UseItemKeys.uuid]] = useItem

                if useItem[UseItemKeys.uuid] not in self.bagUUIDList:
                    self.bagUUIDList.append(useItem[UseItemKeys.uuid])

        KBEngine.executeRawDatabaseCommand(sql,cb)
        pass

    # 增加消耗品
    def addUse(self, configID, count):
        # 1、是否可以合并
        togetherCount = 1
        useConfig = itemsIndex[configID]
        if useConfig["togetherCount"] != 0:
            togetherCount = useConfig["togetherCount"]

        if togetherCount <= 1:
            for i in range(count):
                self.__insertUse(configID, count)
        else:
            self.__updateUse(configID, count)

    # 减少消耗品
    def decUses(self, uuid, count):
        if uuid not in self.useContainer:
            self.onUseError(UseModuleError.Use_not_exist)
            return

        curCount = self.useContainer[uuid]["amount"]
        itemID = self.useContainer[uuid]["itemID"]
        if curCount < count:
            self.onUseError(UseModuleError.Use_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemUses", setMap, filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.useContainer[uuid]["amount"] = curCount - count

                self.noticeClientBagUpdate(uuid,itemID , curCount - count)

                return

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemUses", filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                del self.useContainer[uuid]
                self.writeToDB()

                self.noticeClientBagUpdate(uuid, itemID, 0)

                return

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertUse(self, configID, count=1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemUses", rowValueMap)

        @util.dbDeco
        def cb(result, rownum, error):
            del rowValueMap["roleID"]
            self.useContainer[rowValueMap["UUID"]] = rowValueMap

            self.noticeClientBagUpdate(rowValueMap["UUID"], configID, count)

            self.writeToDB()
            return True

        KBEngine.executeRawDatabaseCommand(sql, cb)


    def __updateUse(self, configID, addCount):

        isFind = False
        # 1、是否存在
        for item in self.useContainer.values():
            if item["itemID"] != configID:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemUses", setMap, filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.useContainer[item["UUID"]]["amount"] = curCount + addCount
                self.noticeClientBagUpdate(item["UUID"], configID, curCount + addCount)


            KBEngine.executeRawDatabaseCommand(sql, cb)
            break
        if isFind == False:
            return self.__insertUse(configID, addCount)
        else:
            return True

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def onClientUse(self,uuid,num):
        # 1、验证是否存在
        if uuid not in self.useContainer:
            self.onUseError(UseModuleError.Use_not_exist)
            return
        # 2、验证数量

        curCount = self.useContainer[uuid][UseItemKeys.amount]
        if curCount < num:
            self.onUseError(UseModuleError.Use_not_enough)
            return False

        # 扣除成功
        self.decUses(uuid,num)

        # 增加属性
        itemID = self.useContainer[uuid][UseItemKeys.itemID]
        addPropName =  itemsUseConfig[itemID][UseItemKeys.addPropName]


        value = getattr(self, addPropName)
        f = str(value) + "+50"
        result = eval(f)

        self.addPropValue(addPropName,result)

        pass

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------

class UseItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"

    addPropName = "addPropName"

if __name__ == "__main__":

    x = 0.002 * util.randFunc()*7000

    y = (0.001 + x)

    print(x)
    print(y)