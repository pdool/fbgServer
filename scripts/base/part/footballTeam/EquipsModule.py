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
装备模块
"""
class EquipsModule:

    def __init__(self):
        # 球员碎片容器
        self.equipsContainer = {}
    def loadEquips(self):
        colTupe = ("sm_UUID", "sm_itemID","sm_amount","sm_shoot","sm_pass","sm_reel","sm_defend","sm_trick","sm_steal"
                   ,"sm_controll","sm_keep")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemEquips", colTupe, filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("EquipModule  loadEquips")
            if result is None:
                return

            for i in range(len(result)):
                equipItem = {}
                equipItem[EquipItemKeys.itemType] = ItemTypeEnum.Equips

                equipItem[EquipItemKeys.uuid]       = int(result[i][0])
                equipItem[EquipItemKeys.itemID]     = int(result[i][1])
                equipItem[EquipItemKeys.amount]     = int(result[i][2])
                equipItem[EquipItemKeys.shoot]      = int(result[i][3])
                equipItem[EquipItemKeys.passBall]   = int(result[i][4])
                equipItem[EquipItemKeys.reel]       = int(result[i][5])
                equipItem[EquipItemKeys.defend]     = int(result[i][6])
                equipItem[EquipItemKeys.trick]      = int(result[i][7])
                equipItem[EquipItemKeys.steal]      = int(result[i][8])
                equipItem[EquipItemKeys.controll]   = int(result[i][9])
                equipItem[EquipItemKeys.keep]       = int(result[i][10])


                self.equipsContainer[equipItem[EquipItemKeys.uuid]] = equipItem

        KBEngine.executeRawDatabaseCommand(sql, cb)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加装备
    def addEquip(self, configID, count = 1):
        # 1、是否可以合并
        togetherCount = 1
        equipConfig = itemsIndex[configID]
        if equipConfig["togetherCount"] != 0:
            togetherCount = equipConfig["togetherCount"]

        if togetherCount == 1:
            self.__insertEquip(configID, count)
        else:
            self.__updateEquips(configID, count)

    # 减少减少
    def decEquip(self, uuid, count):
        if uuid not in self.EquipsContainer:
            self.onEquipError(EquipModuleError.Equip_not_exist)
            return

        curCount = self.EquipsContainer[uuid]["amount"]

        if curCount < count:
            self.onEquipError(EquipModuleError.Equip_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                self.EquipsContainer[uuid]["amount"] = curCount - count

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemEquips", filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                del self.EquipsContainer[uuid]
                self.bagUUIDList.remove(uuid)
                return

            KBEngine.executeRawDatabaseCommand(sql, cb)

    def __insertEquips(self, configID, count=1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap[EquipItemKeys.roleID] = self.databaseID
        rowValueMap[EquipItemKeys.uuid] = KBEngine.genUUID64()
        rowValueMap[EquipItemKeys.itemID] = configID
        rowValueMap[EquipItemKeys.amount] = count

        itemEquipConfig = itemsEquipConfig[configID]

        rowValueMap[EquipItemKeys.shoot] = itemEquipConfig[EquipItemKeys.shoot]
        rowValueMap[EquipItemKeys.passBall] = itemEquipConfig[EquipItemKeys.passBall]
        rowValueMap[EquipItemKeys.reel] = itemEquipConfig[EquipItemKeys.reel]
        rowValueMap[EquipItemKeys.defend] = itemEquipConfig[EquipItemKeys.defend]
        rowValueMap[EquipItemKeys.trick] = itemEquipConfig[EquipItemKeys.trick]
        rowValueMap[EquipItemKeys.steal] = itemEquipConfig[EquipItemKeys.steal]
        rowValueMap[EquipItemKeys.controll] = itemEquipConfig[EquipItemKeys.controll]
        rowValueMap[EquipItemKeys.keep] = itemEquipConfig[EquipItemKeys.keep]

        sql = util.getInsertSql("tbl_ItemEquips", rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onPieceError(1)
                return
            else:
                self.EquipsContainer[rowValueMap["UUID"]] = rowValueMap
                self.bagUUIDList.append(rowValueMap["UUID"])
                self.writeToDB()
                return

        KBEngine.executeRawDatabaseCommand(sql, cb)

        pass

    def __updateEquips(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.EquipsContainer.values():
            if item["itemID"] != configID:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

            def cb(result, rownum, error):
                self.EquipsContainer[item["UUID"]]["amount"] = curCount + addCount

            KBEngine.executeRawDatabaseCommand(sql, cb)

        if isFind == True:
            return
        return self.__insertEquip(configID, addCount)


    def __updateEquipProps(self,uuid,setMap):

        filterMap = {"roleID": self.databaseID, "UUID": uuid}
        sql = util.getUpdateSql("tbl_ItemEquips", setMap, filterMap)

        def cb(result, rownum, error):
            if error is not None:
                return False
            item = self.EquipsContainer[uuid]

            for k,v in setMap.items():
                item[k] = v

            return True
        KBEngine.executeRawDatabaseCommand(sql,cb)



class EquipItemKeys:

    roleID = "roleID"
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"

    shoot = "shoot"
    passBall ="pass"
    reel = "reel"
    defend = "defend"
    trick = "trick"
    steal = "steal"
    controll = "controll"
    keep = "controll"

