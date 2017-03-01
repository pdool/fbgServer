# -*- coding: utf-8 -*-
import equipMake
import itemsEquip
from itemsConfig import itemsIndex
from KBEDebug import *

__author__ = 'wangl'
__createTime__  = '2017年2月17日'
"""
装备模块
"""
class EquipModule:


    def onEntitiesEnabled(self):


        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 客户端请求球员装备星级

    def onClientGetEquipStar(self,cardID,pos):

        if cardID not in self.cardIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardID)
        for equip_info in card.equip:  # 第一个实例
            if equip_info.pos == pos:
                self.client.onClientStar(equip_info.star,equip_info.strongLevel)
        pass

    # 客户端请求背包装备星级
    def onClientGetBagEquipStar(self,uuid):

        if uuid not in self.EquipsContainer:
            # self.onEquipError(EquipModuleError.Equip_not_exist)
            return

        euqipInfo = self.EquipsContainer[uuid]

        self.client.onClientStar(euqipInfo.star, euqipInfo.strongLevel)

        pass
    # 脱装备
    def onClientTakeOffEquip(self,cardId,pos):
        if cardId not in self.cardIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)
        for equip_info in card.equip:  # 第一个实例
            if equip_info.pos == pos:
                self.takeOffEquip(equip_info)
                card.equip.remove(equip_info)

                card.writeToDB()
                self.writeToDB()
            break
    # 制作装备
    def onClientMakeEquip(self,equip_id):

        if equip_id not in equipMake.EquipMakeConfig:
            ERROR_MSG("equip_id not exist")
            return
        equip_make = equipMake.EquipMakeConfig[equip_id]
        equip_cost_info = equip_make["cost"]

        for itemId,num in equip_cost_info.items():
            have = self.getItemNumByItemID(itemId)
            if have < num :
                ERROR_MSG("--------- num bu zu------- have   " + str(have) + "   need  "+ str(num))
                return

        for itemId, num in equip_cost_info.items():
           if self.decItem(itemId,num) == False:
               ERROR_MSG("dec fail")
               return


        self.putItemInBag(equip_id,1)
        ERROR_MSG("add succ")

        self.client.makeEquipSucc()





    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    # 装备

if __name__ == "__main__":
    print(__file__)
    pass




















