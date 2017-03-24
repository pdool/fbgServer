# -*- coding: utf-8 -*-
import random

import equipMake
import equipStarConfig
import equipStrongConfig
import equipStrongCritConfig
import itemsEquip
import itemsDiamond
import gemCompoundConfig
from ErrorCode import EquipModuleError
from ErrorCode import DiamondModuleError
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
            value["gem1"] = pair["gem1"]
            value["gem2"] = pair["gem2"]
            value["gem3"] = pair["gem3"]
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
                    break

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
                self.cardPropCompute(2, card, equip_info)
                break

        self.client.takeOffEquipSucc(cardId)
        card.writeToDB()
        self.writeToDB()
        pass

    # 穿装备
    def onClientPutOnEquip(self,cardId,equipUUId):
        #  判断球员是否存在
        if cardId not in self.cardIDList:
            return
        # 判断背包装备是否存在
        card = KBEngine.entities.get(cardId)

        if equipUUId not in self.equipsContainer:
            self.client.onEquipError(EquipModuleError.Equip_not_exist)
            return
        euqip_data = self.equipsContainer[equipUUId]

        put_on_equip = itemsEquip.itemsEquipConfig[euqip_data["itemID"]]

        # 脱掉之前位置装备
        for equip_info in card.equips:
            item_info = itemsEquip.itemsEquipConfig[equip_info["itemID"]]
            if item_info["position"] == put_on_equip["position"]:
                self.takeOffEquip(equip_info)
                card.equips.remove(equip_info)
                break

        paramMap = {}
        paramMap["UUID"] = euqip_data["UUID"]
        paramMap["itemID"] = euqip_data["itemID"]
        paramMap["amount"] = euqip_data["amount"]
        paramMap["star"]= euqip_data["star"]
        paramMap["strongLevel"] = euqip_data["strongLevel"]
        paramMap["gem1"] = euqip_data["gem1"]
        paramMap["gem2"] = euqip_data["gem2"]
        paramMap["gem3"] = euqip_data["gem3"]



        self.decEquip(euqip_data["UUID"],1)
        card.equips.append(paramMap)

        self.cardPropCompute(1, card, paramMap)
        self.client.putOnEquipSucc(cardId)

        card.writeToDB()
        self.writeToDB()
        pass


    # 制作装备
    def onClientMakeEquip(self,equip_id):

        if equip_id not in equipMake.EquipMakeConfig:
            ERROR_MSG(str(equip_id) + "  is not in  equipMake config ")
            return


        equip_make = equipMake.EquipMakeConfig[equip_id]
        equip_cost_info = equip_make["cost"]

        make_cost = equip_make["money"]
        if self.euro < make_cost:
            self.client.onEquipError(EquipModuleError.Equip_not_euro_enough)
            return

        for itemId,num in equip_cost_info.items():
            have = self.getItemNumByItemID(itemId)
            if have < num :
                ERROR_MSG("--------- num bu zu------- have   " + str(have) + "   need  "+ str(num) + "   " + str(itemId))
                self.client.onEquipError(EquipModuleError.Equip_make_material_not_enough)
                return

        for itemId, num in equip_cost_info.items():
            self.decItem(itemId, num)

        self.putItemInBag(equip_id,1)
        self.writeToDB()

        self.client.makeEquipSucc(equip_id)

    # 装备升星

    def onClientEquipUpStar(self, player_id,equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

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
                self.client.onEquipError(EquipModuleError.Equip_make_material_not_enough)
                return

        for itemId, num in equip_cost_info.items():
            INFO_MSG("--------------itemId-------------" + str(itemId))
            self.decItem(itemId, num)
            # if self.decItem(itemId, num) == False:
            #     ERROR_MSG(m"dec fail")
            #     return

        euqip_data["star"] = euqip_data["star"]+1

        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]

        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
            #     写数据库
            setMap = {"star": euqip_data["star"] }
            self.updateEquipProps(equip_id, setMap)

        self.client.starUpEquipSucc(player_id,value)
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
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        item_id = euqip_data["itemID"]

        if item_id not in itemsEquip.itemsEquipConfig:
            self.client.onEquipError(EquipModuleError.Equip_not_exist)
            return

        equip_info = itemsEquip.itemsEquipConfig[item_id]

        if equip_info is None:
            return

        equip_strong_key = str(equip_info["star"]) + "_" + str(euqip_data["strongLevel"])

        if equip_strong_key not in equipStrongConfig.EquipStrongConfig:
            self.client.onEquipError(EquipModuleError.Equip_not_exist)
            return

        equip_star_up_info = equipStrongConfig.EquipStrongConfig[equip_strong_key]


        if euqip_data["strongLevel"] > equip_info["maxstronglevel"]:
           ERROR_MSG("---------strong>=maxstronglevel------- ")

           return

        if euqip_data["strongLevel"] >= self.level:
           ERROR_MSG("---------strong>self.level------- ")
           return

        strong_cost = equip_star_up_info["cost"]
        if self.euro < strong_cost:
            ERROR_MSG("euro isnot enough-----"+str(strong_cost)+"-----self.euro has----"+str(self.euro))
            self.client.onEquipError(EquipModuleError.Equip_not_euro_enough)
            return

        if(self.vipLevel == 0):
            equip_next_strong = euqip_data["strongLevel"] + 1
        else:
            ran_num = random.randint(0,100)
            equip_crit_info = equipStrongCritConfig.EquipStrongCritConfig[self.vipLevel]
            strike_info = equip_crit_info["strike"]
            strike_list = strike_info.split(";")
            for strike in strike_list:
                data = strike.split(":")
                num = int(data[0])
                levl = int(data[1])
                INFO_MSG("add_strong_lv_ran_num" + str(ran_num) + "------num-----" + str(num) + "------lv" + str(levl))
                if ran_num <= num:
                    equip_next_strong = euqip_data["strongLevel"] + levl
                    break

            INFO_MSG("add_strong_lv_ran_num" + str(ran_num) +"--------vipLevel-----"+str(self.vipLevel)+ "------lv" + str(levl))

        self.euro = self.euro - strong_cost
        euqip_data["strongLevel"] = equip_next_strong

        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]


        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
            #     写数据库
            setMap = {"strongLevel": equip_next_strong}
            self.updateEquipProps(equip_id, setMap)

        self.client.strongUpEquipSucc(player_id,value)
        self.writeToDB()
        pass

     # 装备一键升级 player_id == 0背包装备 equip_id 是uuid
     #  player_id > 0球员装备 equip_id 是 itemID

    def onClientEquipOneKeyUPStrong(self,player_id,equip_id):

        ERROR_MSG(" equip_id       " + str(equip_id))

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        item_id = euqip_data["itemID"]
        equip_info = itemsEquip.itemsEquipConfig[item_id]
        max_strong = equip_info["maxstronglevel"]
        equip_cur_strong =  euqip_data["strongLevel"]
        equip_next_strong =equip_cur_strong
        retItems = []

        while self.euro>0:
            equip_strong_key = str(equip_info["star"]) + "_" + str(equip_next_strong)

            if equip_strong_key not in equipStrongConfig.EquipStrongConfig:
                ERROR_MSG("-----------onClientEquipOneKeyUPStrong -----not exist key ----------------  " + equip_strong_key)
                break

            equip_star_up_info = equipStrongConfig.EquipStrongConfig[equip_strong_key]

            strong_cost = equip_star_up_info["cost"]
            if self.euro < strong_cost:
                self.client.onEquipError(EquipModuleError.Equip_not_euro_enough)
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
                strike_list = strike_info.split(";")
                for strike in strike_list:
                    data = strike.split(":")
                    num = int(data[0])
                    levl = int(data[1])
                    INFO_MSG(
                        "add_strong_lv_ran_num" + str(ran_num) + "------num-----" + str(num) + "------lv" + str(levl))
                    if ran_num <= num:
                        equip_next_strong = euqip_data["strongLevel"] + levl
                        break

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

        euqip_data["strongLevel"] = equip_cur_strong

        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]


        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
        #     写数据库
            setMap= {"strongLevel":equip_cur_strong}
            self.updateEquipProps(equip_id,setMap)

        self.client.getOneKeyUpStrongResult(player_id, value, retItems)
        self.writeToDB()

        pass


    # 请求卸下宝石
    def onClentTakeOffGem(self,index, player_id, equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        gem_pos = "gem" + str(index)
        gem_state = euqip_data[gem_pos]
        if gem_state == 0:
            self.client.onEquipError(DiamondModuleError.Diamond_not_exist)
            return
        elif gem_state < 0:
            self.client.onEquipError(DiamondModuleError.Diamond_hold_not_open)
            return

        euqip_data[gem_pos] = 0

        retItems = []

        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]
        retItems.append(value)

        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
            #     写数据库
            setMap = {gem_pos:0}
            self.updateEquipProps(equip_id, setMap)

        self.putItemInBag(gem_state,1)
        self.client.returnGemResult(player_id,retItems)
        self.writeToDB()


        pass

    # 请求镶嵌宝石
    def onClientInsetGem(self, index, player_id, equip_id, gem_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        if gem_id not in itemsDiamond.itemsDiamondConfig:
            self.client.onEquipError(DiamondModuleError.Diamond_not_exist)
            return


        gem_pos = "gem" + str(index)
        gem_state = euqip_data[gem_pos]
        gem_info = itemsDiamond.itemsDiamondConfig[gem_id]

        if gem_state > 0:
            self.client.onEquipError(DiamondModuleError.Diamond_exist)
            return
        elif gem_state < 0:
            self.client.onEquipError(DiamondModuleError.Diamond_hold_not_open)
            return

        gem_props = ["gem1", "gem2", "gem3"]

        for gem_prop_name in gem_props:
            id = euqip_data[gem_prop_name]
            if id<=0:
                continue
            gem_data = itemsDiamond.itemsDiamondConfig[id]
            if gem_data["propType"] == gem_info["propType"]:
                return


        euqip_data[gem_pos] = gem_id
        retItems = []

        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]
        retItems.append(value)

        self.decItem(gem_id, 1)
        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
            #     写数据库
            setMap = {gem_pos:gem_id}
            self.updateEquipProps(equip_id, setMap)

        self.client.returnGemResult(player_id,retItems)
        self.writeToDB()
        pass

    # 请求宝石开槽
    def onClientGemOpen(self,index, player_id, equip_id):

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        gem_pos = "gem" + str(index)
        gem_state = euqip_data[gem_pos]
        if gem_state >= 0:
            self.client.onEquipError(DiamondModuleError.Diamond_exist_hold)
            return

        equip_id = euqip_data["itemID"]
        if equip_id not in itemsEquip.itemsEquipConfig:
            self.client.onEquipError(EquipModuleError.Equip_not_exist)
            return

        equip_info = itemsEquip.itemsEquipConfig[equip_id]

        material_id = equip_info["openGemMaterial"]
        material_info = equip_info["needOpenHold"]
        need_amount = material_info[index]
        has_amount = self.getItemNumByItemID(material_id)
        ERROR_MSG("-------need_amount------"+str(gem_pos))


        if need_amount > has_amount:
            self.client.onEquipError(DiamondModuleError.Diamond_not_material)
            return

        self.decItem(material_id, need_amount)

        euqip_data[gem_pos] = 0

        retItems = []
        value = {}
        value["UUID"] = euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]
        retItems.append(value)
        if player_id != 0:
            card = KBEngine.entities.get(player_id)
            card.writeToDB()
        else:
            #     写数据库
            setMap = {gem_pos: 0}
            self.updateEquipProps(equip_id, setMap)

        self.client.returnGemResult(player_id, retItems)
        self.writeToDB()

        pass

    # 装备继承 装备来着 ：player_id,equip_id,继承装备ID：select_id
    def onClientEqupInherit(self,player_id,equip_id,select_id):

        select_data =  euqip_data = self.equipsContainer[select_id]

        if player_id == 0:
            euqip_data = self.equipsContainer[equip_id]
        else:
            card = KBEngine.entities.get(player_id)
            for equip_info in card.equips:  # 第一个实例
                if equip_info["itemID"] == equip_id:
                    euqip_data = equip_info
                    break

        strong_lv = euqip_data["strongLevel"]
        select_lv = select_data["strongLevel"]

        inherit_lv = select_data["strongLevel"]-10

        if select_lv-strong_lv < 10:
            self.client.onEquipError(EquipModuleError.Equip_not_strong_enough)
            return

        need_euro = 100*(inherit_lv - strong_lv)

        if self.euro < need_euro:
            self.client.onEquipError(EquipModuleError.Equip_not_euro_enough)
            return

        self.euro = self.euro - need_euro

        euqip_data["strongLevel"] = inherit_lv
        select_data["strongLevel"] = 1


        retItems = []
        value = {}
        value["UUID"] =  euqip_data["UUID"]
        value["itemID"] = euqip_data["itemID"]
        value["amount"] = euqip_data["amount"]
        value["star"] = euqip_data["star"]
        value["strongLevel"] = euqip_data["strongLevel"]
        value["gem1"] = euqip_data["gem1"]
        value["gem2"] = euqip_data["gem2"]
        value["gem3"] = euqip_data["gem3"]

        value1 = {}
        value1["UUID"] = select_data["UUID"]
        value1["itemID"] = select_data["itemID"]
        value1["amount"] = select_data["amount"]
        value1["star"] = select_data["star"]
        value1["strongLevel"] = select_data["strongLevel"]
        value1["gem1"] = select_data["gem1"]
        value1["gem2"] = select_data["gem2"]
        value1["gem3"] = select_data["gem3"]

        retItems.append(value)
        retItems.append(value1)

        # 写数据库
        if player_id != 0:
           card = KBEngine.entities.get(player_id)
           card.writeToDB()
        else:
           setequipMap = {"strongLevel": inherit_lv}
           self.updateEquipProps(euqip_data["itemID"], setequipMap)

        setMap = {"strongLevel": 1}
        self.updateEquipProps(select_id, setMap)

        self.client.returnInheritResult( player_id,retItems)
        self.writeToDB()

        pass


    # 宝石合成 gem_id:uuid

    def onClientGemCompound(self,gem_id):

        item_data = self.diamondsContainer[gem_id]


        if item_data["itemID"] not in gemCompoundConfig.GemCompoundConfig:
            self.client.onEquipError(DiamondModuleError.Diamond_not_compound)
            return

        compound_data = gemCompoundConfig.GemCompoundConfig[item_data["itemID"]]

        need_amount = compound_data["amount"]

        compound_gem_id = compound_data["compundId"]

        have = self.getItemNumByItemID(item_data["itemID"])

        if need_amount > have :
            self.client.onEquipError(DiamondModuleError.Diamond_compound_not_material)
            return

        ERROR_MSG("----------gem_id--------"+str( item_data["itemID"])+"---------has--------"+str(have))

        self.decItem(item_data["itemID"], need_amount)

        self.putItemInBag(compound_gem_id,1)

        self.client.gemCompoundSucc(compound_gem_id)

        self.writeToDB()


        pass

    # 球员属性计算type 1增加属性 2减掉属性
    def cardPropCompute(self,type,card,equipMap):

        item_id = equipMap["itemID"]
        strong  =  equipMap["strongLevel"]
        star    =    equipMap["star"]
        gem1 = equipMap["gem1"]
        gem2 = equipMap["gem2"]
        gem3 = equipMap["gem3"]

        prop_list=["shoot","pass","reel","defend","trick","steal","controll","keep"]
        gem_list=[gem1,gem2,gem3]


        equip_star_key   = str(item_id) + "_" + str(star)
        equip_strong_key = str(star) + "_" + str(strong)

        if equip_star_key not in equipStarConfig.EquipStarConfig:
            ERROR_MSG("-----------EquipStar -----not exist key ----------------  " + equip_star_key)
            return
        if equip_strong_key not in equipStrongConfig.EquipStrongConfig:
            ERROR_MSG("-----------EquipStrong -----not exist key ----------------  " + equip_strong_key)
            return

        equip_base = itemsEquip.itemsEquipConfig[item_id]

        equip_star = equipStarConfig.EquipStarConfig[equip_star_key]

        equip_strong = equipStrongConfig.EquipStrongConfig[equip_strong_key]

        if type == 1:
            for gem in gem_list:
                if gem > 0:
                    gem1_data = itemsDiamond.itemsDiamondConfig[gem1]
                    prop_name = gem1_data["propName"]
                    card[prop_name] = card[prop_name] + gem1_data["propValue"]

            for prop in prop_list:
                 card[prop] = card[prop] + equip_base[prop] + equip_star[prop] + equip_strong[prop]

        if type ==2 :
            for gem in gem_list:
                if gem > 0:
                    gem1_data = itemsDiamond.itemsDiamondConfig[gem1]
                    prop_name = gem1_data["propName"]
                    card[prop_name] = card[prop_name] - gem1_data["propValue"]

            for prop in prop_list:
                card[prop] = card[prop] - equip_base[prop] - equip_star[prop] - equip_strong[prop]



        pass
















    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    # 装备

if __name__ == "__main__":
    print(__file__)
    pass




















