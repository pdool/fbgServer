# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月13日'

import util
from KBEDebug import *
from part.BagModule import ItemTypeEnum
from itemsConfig import itemsIndex
from ErrorCode import MaterialModuleError


"""
材料模块
"""
class MaterialModule:

    def __init__(self):
        # 球员碎片容器
        self.materialContainer = {}
    def loadMaterial(self):

        colTupe = ("sm_UUID", "sm_itemID", "sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemMaterial", colTupe, filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("MaterialModule  loadMaterial")
            if result is None:
                return
            for i in range(len(result)):
                item = {}
                item[MaterialItemKeys.uuid] = int(result[i][0])
                item[MaterialItemKeys.itemID] = int(result[i][1])
                item[MaterialItemKeys.amount] = int(result[i][2])
                item[MaterialItemKeys.itemType] = ItemTypeEnum.Material
                self.materialContainer[item[MaterialItemKeys.uuid]] = item

        KBEngine.executeRawDatabaseCommand(sql, cb)
        pass

    # 增加材料
    def addMaterial(self, configID, count):
        # 1、是否可以合并
        togetherCount = 1
        materialConfig = itemsIndex[configID]
        if materialConfig["togetherCount"] != 0:
            togetherCount = materialConfig["togetherCount"]

        if togetherCount == 1:
            self.__insertUse(configID, count)
        else:
            self.__updateUse(configID, count)

    # 减少材料
    def decMaterial(self, uuid, count):
        if uuid not in self.materialContainer:
            self.onMaterialError(MaterialModuleError.Use_not_exist)
            return

        curCount = self.materialContainer[uuid]["amount"]

        if curCount < count:
            self.onMaterialError(MaterialModuleError.Use_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemMaterial", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                self.materialContainer[uuid]["amount"] = curCount - count

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemMaterial", filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                del self.materialContainer[uuid]
                self.bagUUIDList.remove(uuid)
                self.writeToDB()

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertMaterial(self, configID, count=1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemMaterial", rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onMaterialError(1)
            else:
                self.materialContainer[rowValueMap["UUID"]] = rowValueMap
                self.bagUUIDList.append(rowValueMap["UUID"])
                self.writeToDB()

        KBEngine.executeRawDatabaseCommand(sql, cb)

        pass

    def __updateMaterial(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.materialContainer.values():
            if item["itemID"] != configID:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemMaterial", setMap, filterMap)

            def cb(result, rownum, error):
                self.materialContainer[item["UUID"]]["amount"] = curCount + addCount
                return True

            KBEngine.executeRawDatabaseCommand(sql, cb)

        if isFind == True:
            return
        return self.__insertMaterial(configID, addCount)

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------


        # --------------------------------------------------------------------------------------------
        #                              工具函数
        # --------------------------------------------------------------------------------------------

class MaterialItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"