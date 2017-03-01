# -*- coding: utf-8 -*-
from cardsConfig import cardsConfig
import strikeConfig
from ErrorCode import CardMgrModuleError
from part.BagModule import  ItemTypeEnum
from cardLevelUpgradeConfig import cardLevelUpgradeConfig
from cardLevelUpgradeConfig import levelIniConfig
from itemsUse import itemsUseConfig

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *

class PlayerInfoSelfStatus:
    notSelf = 0
    isSelf = 1

class PlayerInfoTeamStatus:
    notInTeam = 0
    inTeam = 1

class CardMgrModule:

    def __init__(self):
        self.cardIDList = []  # 玩家拥有的卡牌对象内存ID
        self.inTeamcardIDList = []  # 玩家拥有的卡牌对象内存ID
        pass

    def onEntitiesEnabled(self):



        for cardDBID in self.cardDBIDList:
            KBEngine.createBaseFromDBID("Card", cardDBID, self.loadCardCB)
        pass

    """
    baseRef会是一个mailbox或者是新创建的Base实体的直接引用
    dbid会是实体的数据库ID
    wasActive是True则baseRef是已经存在的实体的引用(已经从数据库检出)
    """
    def loadCardCB(self, baseRef, dbid, wasActive):
        if wasActive:
            ERROR_MSG("player :(%i):not create success!" % (self.id))
            return
        if baseRef is None:
            ERROR_MSG("player is not exist")
            return

        card = KBEngine.entities.get(baseRef.id)
        if card is None:
            ERROR_MSG("player create fail")
            return
        if card.isSelf == PlayerInfoSelfStatus.isSelf:
            self.cardID = card.id

        if card.inTeam == 1:
            self.inTeamcardIDList.append(card.id)
        self.cardIDList.append(card.id)


        pass
    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def onClientGetAllCardInfo(self):
        playerInfos = []
        for id in self.cardIDList:
            player = KBEngine.entities.get(id)
            playerInfo = {}
            playerInfo["id"] = id
            playerInfo["configID"] = player.configID
            playerInfo["level"] = player.level
            playerInfo["star"] = player.star
            playerInfo["exp"] = player.exp
            playerInfo["inTeam"] = player.inTeam
            playerInfo["isSelf"] = player.isSelf
            playerInfo["brokenLayer"] = player.brokenLayer
            playerInfo["fightValue"] = player.fightValue
            playerInfo["shoot"] = player.shoot
            playerInfo["defend"] = player.defend
            playerInfo["pass"] = player.passBall
            playerInfo["trick"] = player.trick
            playerInfo["reel"] = player.reel
            playerInfo["steal"] = player.steal
            playerInfo["controll"] = player.controll
            playerInfo["keep"] = player.keep
            playerInfo["tech"] = player.tech
            playerInfo["health"] = player.health
            playerInfos.append(playerInfo)
        self.client.onGetAllCardInfo(playerInfos)

    # 球员升级
    def onClientLevelUp(self,cardID,uuid,num):
        # 1、判断球员是否存在
        # 2、判断道具是否存在
        # 3、判断数量
        # 4、判断等级
        # 5、扣除
        # 6、增加属性
        # 7、保存
        if cardID not in self.cardIDList:
            self.client.onCardError(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardID)

        itemType,item = self.getItemByUUID(uuid)

        if itemType != ItemTypeEnum.Use:
            self.client.onCardError(CardMgrModuleError.Card_not_exp_use)
            return

        if item["amount"] < num:
            self.client.onCardError(CardMgrModuleError.Card_not_enough_use)
            return
        # 当前等级，经验
        level = card.level
        exp = card.exp

        # 等级配置
        levelConfig = levelIniConfig[0]
        # 最高等级
        maxLevel = levelConfig["maxLevel"]

        if level >= maxLevel:
            self.client.onCardError(CardMgrModuleError.Card_is_max_level)
            return



        itemID = item["itemID"]
        addPropName = itemsUseConfig[itemID]["addPropName"]

        if addPropName != "exp":
            self.client.onCardError(CardMgrModuleError.Card_not_exp_use)
            return
        addValueF = itemsUseConfig[itemID]["addValue"]
        resultExp = eval(str(exp) + addValueF)
        

        # 升级配置
        levelUpgradeConfig = cardLevelUpgradeConfig[level + 1]
        upExp = levelUpgradeConfig["maxExp"]

        self.decUses(uuid,num)

        # 循环
        while (resultExp > upExp):
            resultExp = resultExp - upExp

            card.level      = card.level    + 1
            card.shoot      = card.shoot    + levelUpgradeConfig["shoot"]
            card.passBall   = card.passBall + levelUpgradeConfig["pass"]
            card.reel       = card.reel     + levelUpgradeConfig["reel"]
            card.defend     = card.defend   + levelUpgradeConfig["defend"]
            card.trick      = card.trick    + levelUpgradeConfig["trick"]
            card.steal      = card.steal    + levelUpgradeConfig["steal"]
            card.controll   = card.controll + levelUpgradeConfig["controll"]
            card.keep       = card.keep     + levelUpgradeConfig["keep"]

            if card.level + 1 > maxLevel:
                break

            levelUpgradeConfig = cardLevelUpgradeConfig[card.level + 1]
            upExp = levelUpgradeConfig["maxExp"]

        card.exp = resultExp

        card.writeToDB()

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def addCard(self,configID,pos = -1,inTeam = PlayerInfoTeamStatus.notInTeam,isSelf = PlayerInfoSelfStatus.notSelf):

        # 1、判断是否存在

        if configID not in cardsConfig:
            return

        if self.isCardExist(configID) == True:
            return

        config = cardsConfig[configID]

        card = KBEngine.createBaseLocally("Card")

        if card is not None:
            card.roleID = self.databaseID
            card.configID = config["id"]
            card.isSelf = isSelf
            card.star = config["initStar"]
            card.brokenLayer = 1
            card.level = 1
            card.fightValue = 100
            strikeID = card.star * 100 + card.brokenLayer
            card.shoot = config["shoot"] + strikeConfig.StrikeConfig[strikeID]["shoot"]
            card.defend = config["defend"] + strikeConfig.StrikeConfig[strikeID]["defend"]
            card.passBall = config["pass"] + strikeConfig.StrikeConfig[strikeID]["pass"]
            card.trick = config["trick"] + strikeConfig.StrikeConfig[strikeID]["trick"]
            card.reel = config["reel"] + strikeConfig.StrikeConfig[strikeID]["reel"]
            card.steal = config["steal"] + strikeConfig.StrikeConfig[strikeID]["steal"]
            card.controll = config["controll"] + strikeConfig.StrikeConfig[strikeID]["controll"]
            card.keep = config["keep"] + strikeConfig.StrikeConfig[strikeID]["keep"]
            card.tech = config["tech"] + strikeConfig.StrikeConfig[strikeID]["tech"]
            card.health = config["health"] + strikeConfig.StrikeConfig[strikeID]["health"]
            card.inTeam = inTeam

            if inTeam == PlayerInfoTeamStatus.inTeam and card.id not in self.inTeamcardIDList:
                self.inTeamcardIDList.append(card.id)

            if pos != -1:
                card.pos = pos

            card.writeToDB(self.__onCardSaved)
        else:
            DEBUG_MSG("card is not None")

    def __onCardSaved(self, success, card):

        if self.isDestroyed:
            if card is not None:
                card.destroy(True)

        DEBUG_MSG("-------------__onCardSaved succ  ---------------------------")
        self.cardDBIDList.append(card.databaseID)
        self.writeToDB()
        self.cardIDList.append(card.id)

    def isCardExist(self,cardID):
        for id in self.cardIDList:
            player = KBEngine.entities.get(id)

            if player.configID == cardID:
                return True
        return False

class PlayerInfoKeys:
    configID = "configID"
    level = "level"
    star = "star"
    exp = "exp"
    inTeam = "inTeam"



