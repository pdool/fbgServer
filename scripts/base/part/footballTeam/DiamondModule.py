# -*- coding: utf-8 -*-
# from BagModule import ItemTypeEnum

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from ErrorCode import DiamondModuleError
from itemsDiamond import itemsDiamondConfig
from itemsConfig import itemsIndex
from part.BagModule import ItemTypeEnum
"""
装备模块
"""
class DiamondModule:

    def __init__(self):
        # 球员碎片容器
        self.diamondsContainer = {}
    def loadDiamonds(self):
        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemDiamonds", colTupe, filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("DiamondModule  loadDiamonds")
            if result is None:
                return

            for i in range(len(result)):
                pieceItem = {}
                pieceItem[DiamondItemKeys.uuid] = int(result[i][0])
                pieceItem[DiamondItemKeys.itemID] = int(result[i][1])
                pieceItem[DiamondItemKeys.amount] = int(result[i][2])
                pieceItem[DiamondItemKeys.itemType] = ItemTypeEnum.Diamond

                self.diamondsContainer[pieceItem[DiamondItemKeys.uuid]] = pieceItem

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------


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

        if togetherCount == 1:
            self.__insertEquip(configID, count)
        else:
            self.__updateDiamonds(configID, count)
    # 减少宝石
    def decDiamond(self,uuid,count):
        if uuid not in self.diamondsContainer:
            self.onDiamondError(DiamondModuleError.Diamond_not_exist)
            return

        curCount = self.diamondsContainer[uuid]["amount"]

        if curCount < count:
            self.onDiamondError(DiamondModuleError.Diamond_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemDiamonds", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                self.diamondsContainer[uuid]["amount"] = curCount - count
                return

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemDiamonds",filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                del self.diamondsContainer[uuid]
                self.bagUUIDList.remove(uuid)
                return

            KBEngine.executeRawDatabaseCommand(sql, cb)


    def __insertEquip(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemDiamonds",rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onPieceError(1)
            else:
                self.diamondsContainer[rowValueMap["UUID"]] = rowValueMap
                self.bagUUIDList.append(rowValueMap["UUID"])
                self.writeToDB()


        KBEngine.executeRawDatabaseCommand(sql,cb)

    def __updatePieces(self, configID, addCount):

        # 1、是否存在
        for item in self.diamondsContainer.values():
            if item["itemID"] != configID:
                continue

            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID":self.databaseID,"UUID":item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemDiamonds",setMap,filterMap)

            def cb(result, rownum, error):
                self.diamondsContainer[item["UUID"]]["amount"] = curCount + addCount

            KBEngine.executeRawDatabaseCommand(sql,cb)

        return self.__insertEquip(configID, addCount)
class DiamondItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"
