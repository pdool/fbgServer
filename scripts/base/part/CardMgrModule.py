# -*- coding: utf-8 -*-
from cardsConfig import cardsConfig
import strikeConfig
import TimerDefine
from ErrorCode import CardMgrModuleError
from part.BagModule import  ItemTypeEnum
from cardLevelUpgradeConfig import cardLevelUpgradeConfig
from cardLevelUpgradeConfig import levelIniConfig
from itemsUse import itemsUseConfig
import BabyLikingStarConfig
__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
import cardsConfig
import skillLevelConfig
class PlayerInfoSelfStatus:
    notSelf = 0
    isSelf = 1

class PlayerInfoTeamStatus:
    notInTeam = 0
    inTeam = 1

"""
卡牌管理
"""
class CardMgrModule:

    def __init__(self):
        self.cardIDList = []  # 玩家拥有的卡牌对象内存ID
        self.inTeamcardIDList = []  # 玩家拥有的卡牌对象内存ID
        self.benchBallerIDList =[]  #玩家替补席球员ID
        pass

    def onEntitiesEnabled(self):
        self.loadNum = 0
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
            ERROR_MSG("card :(%i):not create success!" % (self.id))
            baseRef.destroyCard()
            KBEngine.createBaseFromDBID("Card", dbid, self.loadCardCB)
            return
        if baseRef is None:
            ERROR_MSG("card is not exist")
            return

        card = KBEngine.entities.get(baseRef.id)
        if card is None:
            ERROR_MSG("card create fail")
            return

        card.playerID = self.id

        if card.isSelf == PlayerInfoSelfStatus.isSelf:

            self.cardID = card.id
            self.level = card.level
        if card.inTeam == 1:
            self.inTeamcardIDList.append(card.id)

        if card.bench == 1:
            self.benchBallerIDList.append(card.id)

        self.cardIDList.append(card.id)
        self.loadNum = self.loadNum + 1

        if self.loadNum == len(self.cardDBIDList):

            self.ballerRelationProp()

        pass

    # def onTimer(self, id, userArg):
    #     if userArg == TimerDefine.Timer_reset_baller_addInfo:
    #     pass

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
            playerInfo["bench"] = player.bench
            playerInfo["pos"] = player.pos
            playerInfo["isSelf"] = player.isSelf
            playerInfo["brokenLayer"] = player.brokenLayer
            playerInfo["fightValue"] = player.fightValue
            playerInfo["shoot"] = player.shoot
            playerInfo["shootM"] = player.shootM
            playerInfo["shootExp"] = player.shootExp
            playerInfo["defend"] = player.defend
            playerInfo["defendM"] = player.defendM
            playerInfo["defendExp"] = player.defendExp
            playerInfo["pass"] = player.passBall
            playerInfo["passBallM"] = player.passBallM
            playerInfo["passBallExp"] = player.passBallExp
            playerInfo["trick"] = player.trick
            playerInfo["trickM"] = player.trickM
            playerInfo["trickExp"] = player.trickExp
            playerInfo["reel"] = player.reel
            playerInfo["reelM"] = player.reelM
            playerInfo["reelExp"] = player.reelExp
            playerInfo["steal"] = player.steal
            playerInfo["stealM"] = player.stealM
            playerInfo["stealExp"] = player.stealExp
            playerInfo["controll"] = player.controll
            playerInfo["controllM"] = player.controllM
            playerInfo["controllExp"] = player.controllExp
            playerInfo["keep"] = player.keep
            playerInfo["keepM"] = player.keepM
            playerInfo["keepExp"] = player.keepExp
            playerInfo["tech"] = player.tech
            playerInfo["health"] = player.health
            playerInfo["strikeNeedCost"] = player.strikeNeedCost
            playerInfo["keepPercent"] = player.keepPercent
            playerInfo["controllPercent"] = player.controllPercent
            playerInfo["shootPercent"] = player.shootPercent
            playerInfo["defendPercent"] = player.defendPercent
            playerInfo["skill1"] = player.skill1
            playerInfo["skill2"] = player.skill2
            playerInfo["skill3"] = player.skill3
            playerInfo["skill4"] = player.skill4
            playerInfo["skill11"] = player.skill11
            playerInfo["skill12"] = player.skill12
            playerInfo["skill13"] = player.skill13
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
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardID)

        itemType,item = self.getItemByUUID(uuid)

        ERROR_MSG("--------uuid ------" + str(uuid) +"  itemType   " + str(itemType))
        if itemType != ItemTypeEnum.Use:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exp_use)
            return

        if item["amount"] < num:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_enough_use)
            return
        # 当前等级，经验
        level = card.level
        exp = card.exp
        if card.level >= self.level:
            self.client.onLevelMax(self.level)
            return
        # 等级配置
        levelConfig = levelIniConfig[0]
        # 最高等级
        maxLevel = levelConfig["maxLevel"]
        if level >= maxLevel:
            self.client.onBallerCallBack(CardMgrModuleError.Card_is_max_level)
            return



        itemID = item["itemID"]
        addPropName = itemsUseConfig[itemID]["addPropName"]

        if addPropName != "exp":
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exp_use)
            return
        addValueF = itemsUseConfig[itemID]["addValue"]
        resultExp = eval(str(exp) + addValueF)

        self.decItem(itemID,num)

        # 循环
        while (card.level <= maxLevel):

            if card.level + 1 > maxLevel:
                card.exp = resultExp
                self.client.onBallerCallBack(CardMgrModuleError.Level_is_sucess)
                break
            # 升级配置
            levelUpgradeConfig = cardLevelUpgradeConfig[card.level]
            upExp = levelUpgradeConfig["maxExp"]
            if card.level >= self.level:
                card.exp = upExp
                self.client.onLevelMax(self.level)
                break
            if resultExp >= upExp:
                card.level      = card.level    + 1
                levelUpgradeConfig = cardLevelUpgradeConfig[card.level]
                card.shoot      = card.shoot    + levelUpgradeConfig["shoot"]
                card.passBall   = card.passBall + levelUpgradeConfig["pass"]
                card.reel       = card.reel     + levelUpgradeConfig["reel"]
                card.defend     = card.defend   + levelUpgradeConfig["defend"]
                card.trick      = card.trick    + levelUpgradeConfig["trick"]
                card.steal      = card.steal    + levelUpgradeConfig["steal"]
                card.controll   = card.controll + levelUpgradeConfig["controll"]
                card.keep       = card.keep     + levelUpgradeConfig["keep"]
            else:
                card.exp = resultExp
                self.client.onBallerCallBack(CardMgrModuleError.Level_is_sucess)
                break;
        card.calcFightValue()
        card.writeToDB()

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def addCard(self,configID,pos,inTeam,isSelf,cb=None):
        # 1、判断是否存在

        if configID not in cardsConfig.cardsConfig:
            return

        if self.isCardExist(configID) == True:
            return

        config = cardsConfig.cardsConfig[configID]

        card = KBEngine.createBaseLocally("Card")

        if card is not None:
            card.roleID = self.databaseID
            card.playerID = self.id
            card.configID = config["id"]
            card.isSelf = isSelf
            card.star = config["initStar"]
            card.brokenLayer = 0
            card.level = 1
            card.fightValue = 100
            card.aShootExp = 0
            card.shootM = 0
            card.aDefendExp = 0
            card.defendM = 0
            card.aPassBallExp = 0
            card.passBallM = 0
            card.aTrickExp = 0
            card.trickM = 0
            card.aReelExp = 0
            card.reelM = 0
            card.aStealExp = 0
            card.stealM = 0
            card.aControllExp = 0
            card.controllM = 0
            card.aKeepExp = 0
            card.keepM = 0
            card.aTechExp = 0
            card.techM = 0
            card.aHealthExp = 0
            card.healthM = 0
            card.strikeNeedCost = 0
            card.keepPercent = 0.0
            card.controllPercent = 0.0
            card.shootPercent = 0.0
            card.defendPercent = 0.0
            levelUpgradeConfig = cardLevelUpgradeConfig[card.level]
            card.shoot = config["shoot"] +  levelUpgradeConfig["shoot"]
            card.defend = config["defend"] + levelUpgradeConfig["defend"]
            card.passBall = config["pass"] + levelUpgradeConfig["pass"]
            card.trick = config["trick"] + levelUpgradeConfig["trick"]
            card.reel = config["reel"] + levelUpgradeConfig["reel"]
            card.steal = config["steal"] + levelUpgradeConfig["steal"]
            card.controll = config["controll"] + levelUpgradeConfig["controll"]
            card.keep = config["keep"] + levelUpgradeConfig["keep"]
            card.tech = config["tech"]
            card.health = config["health"]
            if card.isSelf == 1:
                card.tech = card.tech + float(BabyLikingStarConfig.BabyLikingStarConfig[1]["teamTuple"].split(",")[1])
                card.health = card.health + float(BabyLikingStarConfig.BabyLikingStarConfig[1]["teamTuple"].split(",")[0])
            card.inTeam = inTeam
            skillConfig = cardsConfig.cardsConfig[configID]

            card.skill1 =  skillConfig["skill1ID"] * 100 + 1
            card.skill11 = skillConfig["skill1ID"] * 100 + 1
            card.skill12 = skillConfig["skill12ID"] * 100 + 1
            card.skill13 = skillConfig["skill13ID"] * 100 + 1

            card.skill2 = skillConfig["skill2ID"] * 100 + 1
            card.skill3 = skillConfig["skill3ID"] * 100 + 1
            card.skill4 = skillConfig["skill4ID"] * 100 + 1


            if card.skill3 != 1:
                for itemID, Num in  skillLevelConfig.PropSkillLevelConfig[card.skill3]["addvalue"].items():
                    setattr(card, itemID, getattr(card, itemID) + Num)
            if card.skill4 != 1:
                for itemID, Num in skillLevelConfig.PropSkillLevelConfig[card.skill4]["addvalue"].items():
                    setattr(card, itemID, getattr(card, itemID) + Num)
            if inTeam == PlayerInfoTeamStatus.inTeam and card.id not in self.inTeamcardIDList:
                self.inTeamcardIDList.append(card.id)

            if isSelf == PlayerInfoSelfStatus.isSelf:
                self.cardID = card.id

            card.calcFightValue()

            if pos != -1:
                card.pos = pos

            card.writeToDB(self.__onCardSaved)
            if cb!= None:
                cb(card)
        else:
            DEBUG_MSG("card is not None")

    def UpdateBallerInfo(self, card):
        card.calcFightValue()
        playerInfo = {}
        playerInfo["id"] = card.id
        playerInfo["configID"] = card.configID
        playerInfo["star"] = card.star
        playerInfo["inTeam"] = card.inTeam
        playerInfo["bench"] = card.bench
        playerInfo["pos"] = card.pos
        playerInfo["isSelf"] = card.isSelf
        playerInfo["brokenLayer"] = card.brokenLayer
        playerInfo["fightValue"] = card.fightValue
        playerInfo["level"] = card.level
        playerInfo["exp"] = card.exp
        playerInfo["shoot"] = card.shoot
        playerInfo["shootM"] = card.shootM
        playerInfo["shootExp"] = card.shootExp
        playerInfo["defend"] = card.defend
        playerInfo["defendM"] = card.defendM
        playerInfo["defendExp"] = card.defendExp
        playerInfo["pass"] = card.passBall
        playerInfo["passBallM"] = card.passBallM
        playerInfo["passBallExp"] = card.passBallExp
        playerInfo["trick"] = card.trick
        playerInfo["trickM"] = card.trickM
        playerInfo["trickExp"] = card.trickExp
        playerInfo["reel"] = card.reel
        playerInfo["reelM"] = card.reelM
        playerInfo["reelExp"] = card.reelExp
        playerInfo["steal"] = card.steal
        playerInfo["stealM"] = card.stealM
        playerInfo["stealExp"] = card.stealExp
        playerInfo["controll"] = card.controll
        playerInfo["controllM"] = card.controllM
        playerInfo["controllExp"] = card.controllExp
        playerInfo["keep"] = card.keep
        playerInfo["keepM"] = card.keepM
        playerInfo["keepExp"] = card.keepExp
        playerInfo["tech"] = card.tech
        playerInfo["health"] = card.health
        playerInfo["strikeNeedCost"] = card.strikeNeedCost
        playerInfo["keepPercent"] = card.keepPercent
        playerInfo["controllPercent"] = card.controllPercent
        playerInfo["shootPercent"] = card.shootPercent
        playerInfo["defendPercent"] = card.defendPercent
        playerInfo["skill1"] = card.skill1
        playerInfo["skill2"] = card.skill2
        playerInfo["skill3"] = card.skill3
        playerInfo["skill4"] = card.skill4
        playerInfo["skill11"] = card.skill11
        playerInfo["skill12"] = card.skill12
        playerInfo["skill13"] = card.skill13
        return playerInfo


    def __onCardSaved(self, success, card):

        if self.isDestroyed:
            if card is not None:
                card.destroy(True)
                return

        DEBUG_MSG("-------------__onCardSaved succ  ------card.id-----" + str(card.id)+ "   DBID  " + str(card.databaseID))
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



