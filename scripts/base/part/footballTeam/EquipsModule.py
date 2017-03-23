# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月10日'

import util
from KBEDebug import *
from part.BagModule import ItemTypeEnum
from itemsConfig import itemsIndex
from ErrorCode import EquipModuleError
from itemsEquip import itemsEquipConfig
"""
装备容器
"""
class EquipsModule:

    def __init__(self):
        # 球员碎片容器
        self.equipsContainer = {}
    def loadEquips(self):
        colTupe = ("sm_UUID", "sm_itemID","sm_amount","sm_star","sm_strongLevel","sm_gem1","sm_gem2","sm_gem3")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemEquips", colTupe, filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("EquipModule  loadEquips")

            if result is None:
                return
            for i in range(len(result)):
                equipItem = {}
                equipItem[EquipItemKeys.itemType] = ItemTypeEnum.Equips
                uuid =  int(result[i][0])

                equipItem[EquipItemKeys.uuid]       = uuid
                equipItem[EquipItemKeys.itemID]     = int(result[i][1])
                equipItem[EquipItemKeys.amount]     = int(result[i][2])
                equipItem[EquipItemKeys.star] = int(result[i][3])
                equipItem[EquipItemKeys.strongLevel] = int(result[i][4])
                equipItem[EquipItemKeys.gem1] = int(result[i][5])
                equipItem[EquipItemKeys.gem2] = int(result[i][6])
                equipItem[EquipItemKeys.gem3] = int(result[i][7])

                self.equipsContainer[uuid] = equipItem

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    def addEquipByItemID(self,itemID,num):

        equipInfo = itemsEquipConfig[itemID]
        rowValueMap = {}
        rowValueMap[EquipItemKeys.roleID] = self.databaseID
        rowValueMap[EquipItemKeys.uuid] = KBEngine.genUUID64()
        rowValueMap["itemID"] = itemID
        rowValueMap["amount"] = num
        rowValueMap["star"] = equipInfo["star"]
        rowValueMap["strongLevel"] = 1
        rowValueMap["gem1"] = 0
        rowValueMap["gem2"] = -1
        rowValueMap["gem3"] = -1

        self.addEquipByMap(rowValueMap)


    # 增加装备
    def addEquipByMap(self, paramMap):
        # 1、是否可以合并
        togetherCount = 1
        equipConfig = itemsIndex[paramMap["itemID"]]
        if equipConfig["togetherCount"] != 0:
            togetherCount = equipConfig["togetherCount"]

        if togetherCount <= 1 :
            count = paramMap["amount"]
            paramMap["amount"] = 1
            for i in range(count):
                self.__insertEquips(paramMap)
        else:
            self.__updateEquips(paramMap)

    # 减少减少
    def decEquip(self, uuid, count):
        if uuid not in self.equipsContainer:
            self.onEquipError(EquipModuleError.Equip_not_exist)
            return

        curCount = self.equipsContainer[uuid]["amount"]
        itemID = self.equipsContainer[uuid]["itemID"]
        if curCount < count:
            self.onEquipError(EquipModuleError.Equip_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.equipsContainer[uuid]["amount"] = curCount - count

                self.noticeClientBagUpdate(uuid,itemID , curCount - count)

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemEquips", filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                del self.equipsContainer[uuid]
                self.noticeClientBagUpdate(uuid, itemID, 0)
                return

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertEquips(self, paramMap):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap[EquipItemKeys.roleID] = self.databaseID
        uuid =  KBEngine.genUUID64()
        rowValueMap[EquipItemKeys.uuid] = uuid
        rowValueMap[EquipItemKeys.itemID] = paramMap["itemID"]
        rowValueMap[EquipItemKeys.amount] = paramMap["amount"]
        rowValueMap[EquipItemKeys.star] = paramMap["star"]
        rowValueMap[EquipItemKeys.strongLevel] = paramMap["strongLevel"]
        rowValueMap[EquipItemKeys.gem1] = paramMap["gem1"]
        rowValueMap[EquipItemKeys.gem2] = paramMap["gem2"]
        rowValueMap[EquipItemKeys.gem3] = paramMap["gem3"]
        sql = util.getInsertSql("tbl_ItemEquips", rowValueMap)

        @util.dbDeco
        def cb(result, rownum, error):
            del rowValueMap["roleID"]
            self.equipsContainer[uuid] = rowValueMap
            self.writeToDB()

            self.noticeClientBagUpdate(rowValueMap["UUID"], paramMap["itemID"],  paramMap["amount"])

            return

        KBEngine.executeRawDatabaseCommand(sql, cb)

        pass

    def __updateEquips(self, paramMap):

        # 1、是否存在
        isFind = False
        for item in self.equipsContainer.values():
            if item["itemID"] != paramMap["itemID"]:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + paramMap["amount"]}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.equipsContainer[item["UUID"]]["amount"] = curCount + paramMap["amount"]

                self.noticeClientBagUpdate(item["UUID"], paramMap["itemID"], curCount + paramMap["amount"])

            KBEngine.executeRawDatabaseCommand(sql, cb)
            break

        if isFind == True:
            return
        return self.__insertEquip(paramMap )


    def updateEquipProps(self,uuid,setMap):

        filterMap = {"roleID": self.databaseID, "UUID": uuid}
        sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            item = self.equipsContainer[uuid]

            for k,v in setMap.items():
                item[k] = v

            return True
        KBEngine.executeRawDatabaseCommand(sql,cb)


    def takeOffEquip(self,equipInfo):
        paramMap = {}
        paramMap[EquipItemKeys.itemID] = equipInfo["itemID"]
        paramMap[EquipItemKeys.amount] = equipInfo["amount"]
        paramMap[EquipItemKeys.star] = equipInfo["star"]
        paramMap[EquipItemKeys.strongLevel] = equipInfo["strongLevel"]
        paramMap[EquipItemKeys.gem1] = equipInfo["gem1"]
        paramMap[EquipItemKeys.gem2] = equipInfo["gem2"]
        paramMap[EquipItemKeys.gem3] = equipInfo["gem3"]

        paramMap["count"]  = 1
        self.addEquipByMap(equipInfo)







class EquipItemKeys:

    roleID = "roleID"
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"
    star     ="star"
    strongLevel ="strongLevel"
    gem1="gem1"
    gem2 = "gem2"
    gem3 = "gem3"

    shoot = "shoot"
    passBall ="pass"
    reel = "reel"
    defend = "defend"
    trick = "trick"
    steal = "steal"
    controll = "controll"
    keep = "controll"

