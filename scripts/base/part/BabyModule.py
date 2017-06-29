# -*- coding: utf-8 -*-
import datetime
import traceback
from ErrorCode import BabyModuleError
import TimerDefine
from BagConfig import BagConfig
from itemsConfig import itemsIndex
import CommonConfig
import ClothesConfig
import ClothesLevelConfig
import ClothesSlevelConfig
import ClothesInheritConfig
import UseEquipConfig
import BabyTouchItemConfig
import BabyLikingStarConfig
import ClothesMapConfig
import util
import itemsUse
import gameShopConfig
from KBEDebug import *

"""
足球宝贝模块
"""


class BabyModule:
    def onEntitiesEnabled(self):
        if self.babyDBID != 0:
            KBEngine.createBaseFromDBID("Baby", self.babyDBID, self.loadBabyCB)
        offset = util.getLeftSecsToNextHMS(0, 0, 0)
        self.addTimer(offset, 24 * 60 * 60, TimerDefine.Timer_reset_lottery_free_times)
        self.addTimer(offset, 24 * 60 * 60, TimerDefine.Timer_reset_shop_item)
        """
           baseRef会是一个mailbox或者是新创建的Base实体的直接引用
           dbid会是实体的数据库ID
           wasActive是True则baseRef是已经存在的实体的引用(已经从数据库检出)
           """

    def loadBabyCB(self, baseRef, dbid, wasActive):
        if wasActive:
            ERROR_MSG("Baby :(%i):not create success!" % (self.id))
            baseRef.destroyBaby()
            KBEngine.createBaseFromDBID("Baby", self.babyDBID, self.loadBabyCB)
            return
        if baseRef is None:
            ERROR_MSG("Baby is not exist")
            return

        baby = KBEngine.entities.get(baseRef.id)
        if baby is None:
            ERROR_MSG("Baby create fail")
            return

        baby.playerID = self.id

        self.babyID = baby.id

        pass

    def destroyBaby(self):
        self.destroy()

    def onTimer(self, id, userArg):
        if userArg == TimerDefine.Timer_reset_lottery_free_times:
            baby = KBEngine.entities.get(self.babyID)
            if baby is None:
                self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
                return
            baby.bodyIndex = 0
            baby.headIndex = 0
            baby.chestIndex = 0
            baby.legIndex = 0
            baby.handIndex = 0
            baby.closeTouch = BabyTouchItemConfig.BabyTouchItemConfig[102034]["times"]
        elif userArg == TimerDefine.Timer_reset_baby_fullTime:
            self.delTimer(id)
            baby.isFullTime = 0
            configs = CommonConfig.CommonConfig[5]
            index = baby.liking // configs["value"]
            config = CommonConfig.CommonConfig[4]
            time = config["value"]
            baby.liking = BabyLikingStarConfig.BabyLikingStarConfig[5]["liking"]
            if baby.liking % configs["value"] > 0:
                index = index + 1
            baby.likingTime = index * time * 60
            self.client.onFullTimeOver(0, baby.likingTime)
            self.Timer_reset_baby_liking = baby.addTimer(time * 60, time * 60, TimerDefine.Timer_reset_baby_liking)
            self.Timer_reset_baby_likingTime = baby.addTimer(0, 1, TimerDefine.Timer_reset_baby_likingTime)
        elif userArg == TimerDefine.Timer_reset_shop_item:
            for Item in self.gameShopItemList:
                config = gameShopConfig.gameShopConfig[Item["itemID"]]
                Item["limitTimes"] = config["limitTimes"]

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def onClientTouchBabyInfo(self, itemID, bodyIndex, star):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        if itemID == 102034:
            if baby.closeTouch > 0:
                baby.closeTouch = baby.closeTouch - 1
            else:
                return
        else:
            itemCount = self.getItemNumByItemID(itemID)
            if itemCount < 1:
                self.client.onBabyCallBack(BabyModuleError.Material_not_enough)
                return
            self.decItem(itemID, 1)
        liking = int(itemsUse.itemsUseConfig[itemID]["addValue"]) * int(
            BabyLikingStarConfig.BabyLikingStarConfig[star]["addPercent"])
        config = CommonConfig.CommonConfig[4]
        time = config["value"]
        if baby.liking == 0 and baby.likingTime == 0:
            baby.likingTime = time * 60
            baby.liking = baby.liking + liking
            self.Timer_reset_baby_liking = baby.addTimer(time * 60, time * 60, TimerDefine.Timer_reset_baby_liking)
            self.Timer_reset_baby_likingTime = baby.addTimer(1, 1, TimerDefine.Timer_reset_baby_likingTime)
        else:
            if baby.liking >= BabyLikingStarConfig.BabyLikingStarConfig[5]["liking"]:
                self.client.onBabyCallBack(BabyModuleError.Liking_is_max)
                return
            configs = CommonConfig.CommonConfig[5]
            index = baby.liking // configs["value"]
            baby.liking = baby.liking + liking
            nowindex = baby.liking // configs["value"]
            baby.likingTime = baby.likingTime + (nowindex - index) * time * 60
            if baby.liking >= BabyLikingStarConfig.BabyLikingStarConfig[5]["liking"]:
                baby.liking = BabyLikingStarConfig.BabyLikingStarConfig[5]["liking"]
                baby.fullTime = util.getCurrentTime()
                baby.periodTime = util.getCurrentTime()
                baby.isFullTime = 1
                self.addTimer(6 * 60 * 60, 60 * 60, TimerDefine.Timer_reset_baby_fullTime)
                baby.delTimer(self.Timer_reset_baby_liking)
                baby.delTimer(self.Timer_reset_baby_likingTime)
                self.client.onFullTimeOver(1, baby.liking, baby.fullTime)
                return
            tech = 0.0
            health = 0.0
            for i in range(5):
                info = BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["liking"]
                tech = tech + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[1])
                health = health + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[0])
                if baby.liking <= info:
                    break
            player = KBEngine.entities.get(self.cardID)
            if player.tech != tech or player.health != health:
                player.tech = tech
                player.health = health
                self.client.onUpdateCardInfo(self.UpdateBallerInfo(player))
        self.client.onTouchSucess(baby.liking, baby.likingTime)

    def onClientGetBabyInfo(self):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        self.client.onGetBabyInfo(baby.liking, baby.fullTime, baby.closeTouch, baby.itemTouch, baby.likingTime,
                                  baby.GetRewardList)

    def onClientGetBabyItemInfo(self):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        self.client.onGetBabyItemInfo(baby.itemList)

    def onClientGetMapReward(self, mapID):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        config = ClothesMapConfig.ClothesMapConfig[mapID]
        reward = config["reward"]
        addValue = config["addvalue"]
        for id in baby.GetRewardList:
            if mapID == id:
                self.client.onBabyCallBack(BabyModuleError.Have_GetReward)
                return
        for itemId, num in reward.items():
            self.putItemInBag(itemId, num)
        for name, num in addValue.items():
            add = self.GetObjectValue(self.cardID, name)
            self.SetObjectValue(self.cardID, name, num + add)
        card = KBEngine.entities.get(self.cardID)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))
        baby.GetRewardList.append(mapID)
        self.client.onGetRewardSuceess(mapID)

    # 时装强化
    def onClientClothesLevel(self, configID, equiList):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        clothesItem = None
        for item in baby.itemList:
            if item["configID"] == configID:
                clothesItem = item
                break
        exp = 0
        money = 0
        for i in range(len(equiList)):
            itemID = equiList[i]["itemID"]
            star = equiList[i]["number"]
            # 判断碎片数量
            itemCount = self.getItemNumByItemID(itemID)
            if itemCount < 1:
                self.client.onBallerCallBack(BabyModuleError.Material_not_enough)
                return
            exp = exp + UseEquipConfig.UseEquipConfig[star]["exp"]
            money = money + UseEquipConfig.UseEquipConfig[star]["money"]
        if self.euro >= money:
            self.useEuro(money)
        else:
            self.client.onBabyCallBack(BabyModuleError.Money_not_enough)
            return

        for i in range(len(equiList)):
            itemID = equiList[i]["itemID"]
            self.decItem(itemID, 1)
        level = clothesItem["level"]
        clothesItem["exp"] = clothesItem["exp"] + exp
        if level == clothesItem["maxLevel"]:
            self.client.onBabyCallBack(BabyModuleError.Clothes_level_max)
            return
        levelID = configID + level
        levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
        needExp = levelConfig["needExp"]
        if clothesItem["exp"] < needExp:
            self.client.onLevelSucessCallBack(clothesItem["exp"], level)
            return
        config = ClothesConfig.ClothesConfig[configID]
        isPercentType = config["percentType"]
        firstName = config["firstName"]
        seondName = config["seondName"]
        while (clothesItem["exp"] >= needExp):
            ERROR_MSG("   onClientClothesLevel    while    ")
            if level == clothesItem["maxLevel"]:
                self.client.onBabyCallBack(BabyModuleError.Clothes_level_max)
                break
            level = level + 1
            levelID = configID + level
            levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
            needExp = levelConfig["needExp"]

            # 穿戴状态同步增加主角属性
            if clothesItem["isWear"] == 1:

                self.addPlayerInfo(firstName, levelConfig["firstValue"])

                # 激活时装额外属性
                if level >= config["lockLevel"]:
                    if isPercentType == 0:
                        self.addPlayerInfo(seondName, levelConfig["lockValue"])
                    else:
                        self.addPlayerInfo(seondName + "Percent", levelConfig["lockValue"])
                # 激活时装进阶属性
                if level == config["lockLevel"]:
                    for i in range(config["initStar"], clothesItem["star"] + 1):
                        slevelID = configID + i
                        slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
                        if isPercentType == 0:
                            self.addPlayerInfo(seondName, slevelConfig["lockValue"])
                        else:
                            self.addPlayerInfo(seondName + "Percent", slevelConfig["lockValue"])
        clothesItem["level"] = level

        if clothesItem["isWear"] == 1:
            self.updatePlayerInfo()
        self.client.onLevelSucessCallBack(clothesItem["exp"], level)

    # 时装进阶
    def onClientClothesSlevel(self, configID):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return

        clothesItem = None
        for item in baby.itemList:
            if item["configID"] == configID:
                clothesItem = item
                break

        config = ClothesConfig.ClothesConfig[configID]
        isPercentType = config["percentType"]
        if clothesItem["star"] == config["maxStar"]:
            self.client.onBabyCallBack(BabyModuleError.Clothes_star_max)
            return
        slevelID = configID + clothesItem["star"]
        slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
        slevelCost = slevelConfig["cost"]
        for itemId, num in slevelCost.items():
            itemCount = self.getItemNumByItemID(itemId)
            if itemCount < num:
                self.client.onBabyCallBack(BabyModuleError.Material_not_enough)
                return
        for itemId, num in slevelCost.items():
            self.decItem(itemId, num)

        clothesItem["star"] = clothesItem["star"] + 1
        if clothesItem["isWear"] == 0:
            self.client.onSlevelSucessCallBack(clothesItem["star"])
            return

        # 穿戴状态同步增加主角属性
        slevelID = configID + clothesItem["star"]
        slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]

        firstName = config["firstName"]

        self.addPlayerInfo(firstName, slevelConfig["addvalue"])
        if clothesItem["level"] >= config["lockLevel"]:
            seondName = config["seondName"]

            if isPercentType == 0:
                self.addPlayerInfo(seondName, slevelConfig["lockValue"])
            else:
                self.addPlayerInfo(seondName + "Percent", slevelConfig["lockValue"])
        self.updatePlayerInfo()
        self.client.onSlevelSucessCallBack(clothesItem["star"])

    # 更换时装
    def onClientChangeClothes(self, configID):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        Config = ClothesConfig.ClothesConfig[configID]
        lastType = Config["type"]
        oldItem = None
        newItem = None
        for item in baby.itemList:
            if item["isWear"] == 1 and item["type"] == lastType:
                oldItem = item
            if item["configID"] == configID:
                newItem = item
            if oldItem != None and newItem != None:
                break

        oldItem["isWear"] = 0
        baseValue, percentValue, isPercentType = self.ComputeValue(oldItem)

        oldConfig = ClothesConfig.ClothesConfig[oldItem["configID"]]
        self.decPlayerInfo(oldConfig["firstName"], baseValue)
        if isPercentType == 0:
            self.decPlayerInfo(oldConfig["seondName"], percentValue)
        else:
            self.decPlayerInfo(oldConfig["seondName"] + "Percent", percentValue)

        newItem["isWear"] = 1
        baseValue, percentValue, isPercentType = self.ComputeValue(newItem)

        self.addPlayerInfo(Config["firstName"], baseValue)
        if isPercentType == 0:
            self.addPlayerInfo(Config["seondName"], percentValue)
        else:
            self.addPlayerInfo(Config["seondName"] + "Percent", percentValue)

        self.updatePlayerInfo()
        self.client.onBabyCallBack(BabyModuleError.Change_is_sucess)

    # 时装传承
    def onClientInheritClothes(self, inheritID, beInheritID, chooseItem):
        baby = KBEngine.entities.get(self.babyID)
        if baby is None:
            self.client.onBabyCallBack(BabyModuleError.Baby_not_exist)
            return
        inheritPercent = 0
        if chooseItem == 1:
            itemID = ClothesInheritConfig.ClothesInheritConfig[chooseItem]["cost"]
            itemCount = self.getItemNumByItemID(itemID)
            if itemCount < 1:
                self.client.onBabyCallBack(BabyModuleError.Material_not_enough)
                return
            self.decItem(itemID, 1)

        inheritPercent = 0.0
        inheritPercent = ClothesInheritConfig.ClothesInheritConfig[chooseItem]["percent"]
        inherit = ClothesConfig.ClothesConfig[inheritID]
        inheritFirstName = inherit["firstName"]
        inheritSeondName = inherit["seondName"]

        beInherit = ClothesConfig.ClothesConfig[beInheritID]
        beInheritFirstName = beInherit["firstName"]
        beInheritSeondName = beInherit["seondName"]
        addExp = 0
        inheritItem = None
        beInheritItem = None

        for item in baby.itemList:
            if item["configID"] == inheritID:
                inheritItem = item
            if item["configID"] == beInheritID:
                beInheritItem = item
            if inheritItem != None and beInheritItem != None:
                break
        if inheritItem == None or beInheritItem == None:
            self.client.onBabyCallBack(BabyModuleError.Clothes_not_exist)
            return
        addExp = int(inheritItem["exp"] * inheritPercent)
        needMoney = addExp * 10
        if self.euro < needMoney:
            self.client.onBabyCallBack(BabyModuleError.Money_not_enough)
            return
        self.useEuro(needMoney)

        inheritItem["exp"] = 0
        if inheritItem["isWear"] == 0:
            inheritItem["level"] = 1
        else:
            for i in range(2, inheritItem["level"] + 1):
                levelID = inheritID + i
                levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
                self.decPlayerInfo(inheritFirstName, levelConfig["firstValue"])
                if i >= inherit["lockLevel"]:
                    if inherit["percentType"] == 0:
                        self.decPlayerInfo(inheritSeondName, levelConfig["lockValue"])
                    else:
                        self.decPlayerInfo(inheritSeondName + "Percent", levelConfig["lockValue"])
                if i == inherit["lockLevel"]:
                    for j in range(inherit["initStar"], inheritItem["star"] + 1):
                        slevelID = inheritID + j
                        slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
                        if inherit["percentType"] == 0:
                            self.decPlayerInfo(inheritSeondName, slevelConfig["lockValue"])
                        else:
                            self.decPlayerInfo(inheritSeondName + "Percent", slevelConfig["lockValue"])
            inheritItem["level"] = 1
            self.updatePlayerInfo()

        currentLevel = beInheritItem["level"]
        currentExp = beInheritItem["exp"] + addExp
        levelID = beInheritID + currentLevel
        levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
        needExp = levelConfig["needExp"]
        if currentExp < needExp:
            self.client.onBabyCallBack(BabyModuleError.Inherit_is_sucess)
            return
        while (currentExp >= needExp):
            ERROR_MSG(  "onClientInheritClothes   while    ")
            if currentLevel == beInheritItem["maxLevel"]:
                self.client.onBabyCallBack(BabyModuleError.Clothes_level_max)
                break
            currentLevel = currentLevel + 1
            levelID = beInheritID + currentLevel
            levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
            needExp = levelConfig["needExp"]
            # 穿戴状态同步增加主角属性
            if beInheritItem["isWear"] == 1:

                self.addPlayerInfo(beInheritFirstName, levelConfig["firstValue"])

                # 激活时装额外属性
                if currentLevel >= beInherit["lockLevel"]:
                    if beInherit["percentType"] == 0:
                        self.addPlayerInfo(beInheritSeondName, levelConfig["lockValue"])
                    else:
                        self.addPlayerInfo(beInheritSeondName + "Percent", levelConfig["lockValue"])
                # 激活时装进阶属性
                if currentLevel == beInherit["lockLevel"]:
                    for i in range(beInherit["initStar"], beInheritItem["star"] + 1):
                        slevelID = beInheritID + i
                        slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
                        if beInherit["percentType"] == 0:
                            self.addPlayerInfo(beInheritSeondName, slevelConfig["lockValue"])
                        else:
                            self.addPlayerInfo(beInheritSeondName + "Percent", slevelConfig["lockValue"])

        beInheritItem["level"] = currentLevel
        if currentLevel == beInheritItem["maxLevel"]:
            levelID = beInheritID + currentLevel - 1
            levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
            beInheritItem["exp"] = levelConfig["needExp"]
        else:
            beInheritItem["exp"] = currentExp
        if beInheritItem["isWear"] == 1:
            self.updatePlayerInfo()
        self.client.onBabyCallBack(BabyModuleError.Inherit_is_sucess)

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------
    def ComputeValue(self, item):
        Clothes = ClothesConfig.ClothesConfig[item["configID"]]
        isPercentType = Clothes["percentType"]
        level = item["level"]
        baseValue = 0
        percentValue = 0
        for i in range(1, level + 1):
            levelID = item["configID"] + i
            levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelID]
            baseValue = baseValue + levelConfig["firstValue"]
            if i >= Clothes["lockLevel"]:
                if isPercentType == 0:
                    percentValue = percentValue + levelConfig["lockValue"]
                else:
                    percentValue = 0.0
                    percentValue = percentValue + float(slevelConfig["lockValue"])
        star = item["star"]
        for i in range(Clothes["initStar"], item["star"] + 1):
            slevelID = item["configID"] + item["star"]
            slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
            baseValue = baseValue + slevelConfig["addvalue"]
            if level >= Clothes["lockLevel"]:
                if isPercentType == 0:
                    percentValue = percentValue + slevelConfig["lockValue"]
                else:
                    percentValue = 0.0
                    percentValue = percentValue + float(slevelConfig["lockValue"])
        return baseValue, percentValue, isPercentType

    def addPlayerInfo(self, name, value):
        addvalue = self.GetObjectValue(self.cardID, name) + value
        self.SetObjectValue(self.cardID, name, addvalue)

    def decPlayerInfo(self, name, value):
        decvalue = self.GetObjectValue(self.cardID, name) - value
        self.SetObjectValue(self.cardID, name, decvalue)

    def updatePlayerInfo(self):
        if self.cardID not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        card = KBEngine.entities.get(self.cardID)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))
