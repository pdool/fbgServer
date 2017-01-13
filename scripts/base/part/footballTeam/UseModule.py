# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from part.BagModule import ItemTypeEnum
from itemsConfig import itemsIndex
from ErrorCode import UseModuleError

"""
消耗品模块
"""
class UseModule:

    def __init__(self):
        # 消耗品容器
        self.useContainer = {}
    def loadUse(self):
        colTupe= ("sm_UUID","sm_itemID","sm_amount")
        filterMap = {"sm_roleID":self.databaseID}
        sql = util.getSelectSql("tbl_ItemUses",colTupe,filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("UseModule  loadUseItem")
            if result is None:
                return
            for i in range(len(result)):
                useItem = {}
                useItem[UseItemKeys.uuid] = int(result[i][0])
                useItem[UseItemKeys.itemID] = int(result[i][1])
                useItem[UseItemKeys.amount] = int(result[i][2])
                useItem[UseItemKeys.itemType] = ItemTypeEnum.Use
                self.useContainer[ useItem[UseItemKeys.uuid]] = useItem


        KBEngine.executeRawDatabaseCommand(sql,cb)
        pass

    # 增加消耗品
    def addUse(self, configID, count):
        # 1、是否可以合并
        togetherCount = 1
        useConfig = itemsIndex[configID]
        if useConfig["togetherCount"] != 0:
            togetherCount = useConfig["togetherCount"]

        if togetherCount == 1:
            self.__insertUse(configID, count)
        else:
            self.__updateUse(configID, count)

    # 减少消耗品
    def decUses(self, uuid, count):
        if uuid not in self.useContainer:
            self.onUseError(UseModuleError.Use_not_exist)
            return False

        curCount = self.useContainer[uuid]["amount"]

        if curCount < count:
            self.onUseError(UseModuleError.Use_not_enough)
            return False

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemUses", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return False
                self.useContainer[uuid]["amount"] = curCount - count
                return True

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemUses", filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return False
                del self.useContainer[uuid]
                self.bagUUIDList.remove(uuid)
                self.writeToDB()
                return True

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertUse(self, configID, count=1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemUses", rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onUseError(1)
                return False
            else:
                self.useContainer[rowValueMap["UUID"]] = rowValueMap
                self.bagUUIDList.append(rowValueMap["UUID"])
                self.writeToDB()
                return True

        KBEngine.executeRawDatabaseCommand(sql, cb)

        pass

    def __updateUse(self, configID, addCount):

        # 1、是否存在
        for item in self.useContainer.values():
            if item["itemID"] != configID:
                continue

            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemUses", setMap, filterMap)

            def cb(result, rownum, error):
                self.useContainer[item["UUID"]]["amount"] = curCount + addCount
                return True

            KBEngine.executeRawDatabaseCommand(sql, cb)

        return self.__insertUse(configID, addCount)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------

class UseItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"
