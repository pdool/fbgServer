# -*- coding: utf-8 -*-

__author__ = 'chongxin'
__createTime__  = '2017年1月10日'

import util
from KBEDebug import *
from part.BagModule import ItemTypeEnum
from ErrorCode import EquipModuleError
from itemsEquip import itemsEquipConfig
"""
装备容器
"""
class EquipsContainer:

    def __init__(self):
        # 球员碎片容器
        self.equipsContainer = {}
    def loadEquips(self):
        colTupe = ("sm_UUID", "sm_itemID","sm_amount","sm_star","sm_strongLevel","sm_gem1","sm_gem2","sm_gem3")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemEquips", colTupe, filterMap)
        @util.dbDeco
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
                equipItem[EquipItemKeys.star]       = int(result[i][3])
                equipItem[EquipItemKeys.strongLevel] = int(result[i][4])
                equipItem[EquipItemKeys.gem1]       = int(result[i][5])
                equipItem[EquipItemKeys.gem2]       = int(result[i][6])
                equipItem[EquipItemKeys.gem3]       = int(result[i][7])
                equipItem[EquipItemKeys.state]      = DBState.NoAction
                self.equipsContainer[uuid] = equipItem

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------

    def addEquipByItemID(self,itemID,num = 1):

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

        return self.addEquipByMap(rowValueMap)



    # 增加装备
    def addEquipByMap(self, paramMap):
        # 1、是否可以合并
        num =  paramMap["amount"]
        paramMap["amount"] = 1

        for i in range(num):
            self.__insertEquips(paramMap)

        return True


    # 装备不可堆叠。直接删除就行了
    def decEquip(self, uuid, count = 1):
        if uuid not in self.equipsContainer:
            self.client.onEquipError(EquipModuleError.Equip_not_exist)
            return False

        itemID = self.equipsContainer[uuid]["itemID"]
        if DBState.Del == self.equipsContainer[uuid]["state"]:
            return False

        self.equipsContainer[uuid]["state"] = DBState.Del
        self.noticeClientBagUpdate(uuid, itemID, 0)

        return  True


    # 插入装备
    def __insertEquips(self, paramMap):
        #
        rowValueMap = {}
        uuid =  KBEngine.genUUID64()
        rowValueMap[EquipItemKeys.uuid] = uuid
        rowValueMap[EquipItemKeys.itemID] = paramMap["itemID"]
        rowValueMap[EquipItemKeys.amount] = paramMap["amount"]
        rowValueMap[EquipItemKeys.star] = paramMap["star"]
        rowValueMap[EquipItemKeys.strongLevel] = paramMap["strongLevel"]
        rowValueMap[EquipItemKeys.gem1] = paramMap["gem1"]
        rowValueMap[EquipItemKeys.gem2] = paramMap["gem2"]
        rowValueMap[EquipItemKeys.gem3] = paramMap["gem3"]

        rowValueMap["state"] = DBState.Insert
        self.equipsContainer[uuid] = rowValueMap

        self.noticeClientBagUpdate(rowValueMap["UUID"], paramMap["itemID"],  paramMap["amount"])

        return True



    def updateEquipProps(self,uuid,setMap):

        item = self.equipsContainer[uuid]

        for k in setMap.keys():
            item[k] = setMap[k]
        if item["state"] != DBState.Insert:
            item["state"] = DBState.Update

        return True


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



    # 存储数据库


    def onTimerSyncEquipDB(self):

        delKeys = []
        for item in self.equipsContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertEquipDB(item)
            # 更新
            elif state == DBState.Update:
                self.updateEquipDB(item)
            # 删除
            elif state == DBState.Del:
                self.delEquipDB(item)
                delKeys.append(item["UUID"])

        for key in delKeys:
            del self.equipsContainer[key]

    def insertEquipDB(self, item):
        # 自己写数据库

        rowValueMap = {}
        rowValueMap[EquipItemKeys.roleID] = self.databaseID
        uuid =  item[EquipItemKeys.uuid]
        rowValueMap[EquipItemKeys.uuid] = uuid
        rowValueMap[EquipItemKeys.itemID] = item["itemID"]
        rowValueMap[EquipItemKeys.amount] = item["amount"]
        rowValueMap[EquipItemKeys.star] = item["star"]
        rowValueMap[EquipItemKeys.strongLevel] = item["strongLevel"]
        rowValueMap[EquipItemKeys.gem1] = item["gem1"]
        rowValueMap[EquipItemKeys.gem2] = item["gem2"]
        rowValueMap[EquipItemKeys.gem3] = item["gem3"]

        sql = util.getInsertSql("tbl_ItemEquips", rowValueMap)
        item["state"] = DBState.NoAction
        # ERROR_MSG("Equip  insert DB    " + sql)
        KBEngine.executeRawDatabaseCommand(sql)



    def updateEquipDB(self, item):
        setMap = {}
        setMap[EquipItemKeys.star] = item["star"]
        setMap[EquipItemKeys.strongLevel] = item["strongLevel"]
        setMap[EquipItemKeys.gem1] = item["gem1"]
        setMap[EquipItemKeys.gem2] = item["gem2"]
        setMap[EquipItemKeys.gem3] = item["gem3"]
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}

        item["state"] = DBState.NoAction
        sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)
        KBEngine.executeRawDatabaseCommand(sql)


    def delEquipDB(self, item):
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
        sql = util.getDelSql("tbl_ItemEquips", filterMap)
        KBEngine.executeRawDatabaseCommand(sql)



class EquipItemKeys:

    roleID      = "roleID"
    uuid        = "UUID"
    itemID      = "itemID"
    amount      = "amount"
    itemType    = "itemType"
    star        ="star"
    strongLevel ="strongLevel"
    gem1        ="gem1"
    gem2        = "gem2"
    gem3        = "gem3"
    shoot       = "shoot"
    passBall    ="pass"
    reel        = "reel"
    defend      = "defend"
    trick       = "trick"
    steal       = "steal"
    controll    = "controll"
    keep        = "controll"
    state       = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
