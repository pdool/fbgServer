# -*- coding: utf-8 -*-
import equipMake
import itemsEquip
import equipStarConfig
import equipStrongConfig
import random
import equipStrongCritConfig
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
    # 客户端请求装备列表 cardID == 0 背包装备 >0球员装备
    def onClientGetEquipList(self, cardID):

        if cardID == 0:
            self.onClientGetBagEquipList()
            return

        if cardID not in self.cardIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(cardID)

        self.client.getEquipList(cardID,card.equips)
        pass
    #  客户端请求背包装备列表
    def onClientGetBagEquipList(self):

        bag_retItems = []

        for item in self.equipsContainer:
            if item is None:
                continue
            value = {}
            pair = self.equipsContainer[item]
            value["UUID"] = pair["UUID"]
            value["itemID"] = pair["itemID"]
            value["amount"] = pair["amount"]
            value["star"] = pair["star"]
            value["strongLevel"] = pair["strongLevel"]
            value["gem1"] = 0
            value["gem2"] = 0
            value["gem3"] = 0
            bag_retItems.append(value)

        self.client.getEquipList(0,bag_retItems)
        pass


    # 客户端请求装备星级和强化等级
    # player_id == 0 背包装备 equip_id 是uuid
    #  player_id > 0球员装备 equip_id 是 itemID
    def onClientGetEquipStar(self,player_id,equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info


        self.client.getStarAndStrongLv(euqip_data["star"],euqip_data["strongLevel"])

        pass

    # 脱装备
    def onClientTakeOffEquip(self,cardId,equipId):
        if cardId not in self.cardIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)
        for equip_info in card.equips:  # 第一个实例
            if equip_info["itemID"] == equipId:
                self.takeOffEquip(equip_info)
                card.equips.remove(equip_info)
                INFO_MSG("------------onClientTakeOffEquip-----------" + str(equip_info["itemID"]))

        self.client.takeOffEquipSucc(cardId)

        card.writeToDB()
        self.writeToDB()
        pass

    # 穿装备
    def onClientPutOnEquip(self,cardId,equipUUId):
        #  判断球员是否存在
        if cardId not in self.cardIDList:
            ERROR_MSG("Card_not_exist-----" + str(cardId))
            self.client.returnEquipErrorInfo(2)
            return
        # 判断背包装备是否存在
        card = KBEngine.entities.get(cardId)

        if equipUUId not in self.equipsContainer:
            ERROR_MSG("Equip_not_exist-----" +str(equipUUId))
            self.client.returnEquipErrorInfo(1)
            return
        euqip_data = self.equipsContainer[equipUUId]

        put_on_equip = itemsEquip.itemsEquipConfig[euqip_data["itemID"]]

        # 脱掉之前位置装备
        for equip_info in card.equips:
            item_info = itemsEquip.itemsEquipConfig[equip_info["itemID"]]
            if item_info["position"] == put_on_equip["position"]:
                self.takeOffEquip(equip_info)
                card.equips.remove(equip_info)
                INFO_MSG("------------TakeOffEquip-----------"+str(equip_info["itemID"]))

        paramMap = {}
        paramMap["UUID"] = euqip_data["UUID"]
        paramMap["itemID"] = euqip_data["itemID"]
        paramMap["amount"] = euqip_data["amount"]
        paramMap["star"]= euqip_data["star"]
        paramMap["strongLevel"] = euqip_data["strongLevel"]
        paramMap["gem1"] = 0
        paramMap["gem2"] = 0
        paramMap["gem3"] = 0
        self.decEquip(euqip_data["UUID"],1)
        card.equips.append(paramMap)

        self.client.putOnEquipSucc(cardId)

        card.writeToDB()
        self.writeToDB()
        pass


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
        self.writeToDB()

        self.client.makeEquipSucc(equip_id)

    # 背包装备升星

    def onClientBagEquipUpStar(self, uuid):

        if uuid not in self.equipsContainer:
            # self.onEquipError(EquipModuleError.Equip_not_exist)
            return

        euqip_data = self.equipsContainer[uuid]
        item_id = euqip_data["itemID"]
        equip_next_star = euqip_data["star"] + 1

        equip_info = itemsEquip.itemsEquipConfig[item_id]

        equip_star_key = str(item_id) + "_" + str(euqip_data["star"])
        equip_star_up_info = equipStarConfig.EquipStarConfig[equip_star_key]

        if equip_next_star > equip_info["maxStar"]:
            ERROR_MSG("---------star>=maxStar------- ")
            return

        equip_cost_info = equip_star_up_info["cost"]

        for itemId, num in equip_cost_info.items():
            have = self.getItemNumByItemID(itemId)
            if have < num:
                ERROR_MSG("--------- num bu zu------- have   " + str(have) + "   need  " + str(num))
                return

        for itemId, num in equip_cost_info.items():
            INFO_MSG("--------------itemId-------------" + str(itemId))
            if self.decItem(itemId, num) == False:
                ERROR_MSG("dec fail")
                return

        euqip_data["star"] = euqip_data["star"]+1

        self.client.starUpEquipSucc(equip_next_star,0)
        self.writeToDB()
        pass

     # 装备升级 player_id == 0背包装备 equip_id 是uuid
     #  player_id > 0球员装备 equip_id 是 itemID
    def onClientEquipUpStrongLv(self,player_id,equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info.itemID == equip_id:
                    euqip_data = equip_info

        item_id = euqip_data["itemID"]
        equip_info = itemsEquip.itemsEquipConfig[item_id]
        equip_strong_key = str(item_id) + "_" + str(euqip_data["strongLevel"])
        equip_star_up_info = equipStrongConfig.EquipStrongConfig[equip_strong_key]
        if euqip_data["strongLevel"] > equip_info["maxstronglevel"]:
           ERROR_MSG("---------strong>=maxstronglevel------- ")
           self.client.returnEquipErrorInfo(4)

           return

        if euqip_data["strongLevel"] >= self.level:
           ERROR_MSG("---------strong>self.level------- ")
           self.client.returnEquipErrorInfo(5)
           return

        strong_cost = equip_star_up_info["cost"]
        if self.euro < strong_cost:
            ERROR_MSG("euro isnot enough-----"+str(strong_cost)+"-----self.euro has----"+str(self.euro))
            return

        if(self.vipLevel == 0):
            equip_next_strong = euqip_data["strongLevel"] + 1
        else:
            ran_num = random.randint(0,100)
            equip_crit_info = equipStrongCritConfig.EquipStrongCritConfig[self.vipLevel]
            strike_info = equip_crit_info["strike"]
            for num, levl in strike_info.items():
                if ran_num <= num:
                    equip_next_strong = euqip_data["strongLevel"] + levl

            INFO_MSG("add_strong_lv_ran_num" + str(ran_num) + "------lv" + str(levl))

        self.euro = self.euro - strong_cost
        euqip_data["strongLevel"] = equip_next_strong
        self.client.strongUpEquipSucc(equip_next_strong,player_id)

        self.writeToDB()
        pass

     # 装备一键升级 player_id == 0背包装备 equip_id 是uuid
     #  player_id > 0球员装备 equip_id 是 itemID

    def onClientEquipOneKeyUPStrong(self,player_id,equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info.itemID == equip_id:
                    euqip_data = equip_info

        item_id = euqip_data["itemID"]
        equip_info = itemsEquip.itemsEquipConfig[item_id]
        max_strong = equip_info["maxstronglevel"]
        equip_cur_strong =  euqip_data["strongLevel"]
        equip_next_strong =equip_cur_strong
        retItems = []

        while self.euro>0:
            equip_strong_key = str(item_id) + "_" + str(equip_next_strong)
            equip_star_up_info = equipStrongConfig.EquipStrongConfig[equip_strong_key]
            strong_cost = equip_star_up_info["cost"]
            if self.euro < strong_cost:
                ERROR_MSG("euro isnot enough-----" + str(strong_cost) + "-----self.euro has----" + str(self.euro))
                break

            if equip_cur_strong>= self.level:
                ERROR_MSG("---------strong>=self.level------- ")
                break

            if equip_cur_strong >= max_strong:
                ERROR_MSG("---------strong>=maxstronglevel------- ")
                break

            if (self.vipLevel <= 0):
                equip_next_strong = equip_cur_strong + 1
            else:
                ran_num = random.randint(0, 100)
                equip_crit_info = equipStrongCritConfig.EquipStrongCritConfig[self.vipLevel]
                strike_info = equip_crit_info["strike"]
                for num, levl in strike_info.items():
                    if ran_num <= num:
                        equip_next_strong = equip_cur_strong + levl

            if equip_next_strong >= max_strong:
                equip_next_strong = max_strong

            self.euro = self.euro - strong_cost
            euqip_data["strongLevel"] = equip_next_strong

            value = {}
            value["preStrong"] =equip_cur_strong
            value["nextStrong"] = equip_next_strong
            value["cost"] = strong_cost

            retItems.append(value)

            equip_cur_strong = equip_next_strong

        self.client.getOneKeyUpStrongResult(player_id,equip_cur_strong,retItems)
        self.writeToDB()


        pass














    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    # 装备

if __name__ == "__main__":
    print(__file__)
    pass




















