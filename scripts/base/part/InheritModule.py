# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *
from InheritConfig import InheritConfig
from ErrorCode import CardMgrModuleError
from cardLevelUpgradeConfig import cardLevelUpgradeConfig
from cardLevelUpgradeConfig import levelIniConfig
import shopConfig

__author__ = 'yanghao'

if __name__ == "__main__":

    pass


class InheritModule:
    def __init__(self):
        pass

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    def OnClientInherit(self, cardId, inHeriterId, pieceID, materialId):

        # 判断球员是否存在
        if cardId not in self.cardIDList or inHeriterId not in self.cardIDList:
            self.BallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        # 判断选择传承者的是不是跟被传承者一样
        if cardId == inHeriterId:
             self.BallerCallBack(CardMgrModuleError.InHerit_is_not_self)
             return
        card = KBEngine.entities.get(cardId)

        inHeriter = KBEngine.entities.get(inHeriterId)

        # 判断是不是主角
        if card.isSelf == 1:
             self.BallerCallBack(CardMgrModuleError.InHerit_is_not_main)
             return

        # 判断等级
        if card.level <= inHeriter.level:
             self.BallerCallBack(CardMgrModuleError.InHerit_level_is_enough)
             return

        # 传承配置
        config = InheritConfig[materialId]

        #判断金钱是否足够
        money = config["money"]
        if self.euro < money:
            self.BallerCallBack(CardMgrModuleError.Money_not_enough)
            return
        self.useEuro(money)
        # 判断需要道具的时候道具数量是否足够
        if materialId > 0:
            itemCount = self.getItemNumByItemID(materialId)
            if itemCount < 1:
                self.BallerCallBack(CardMgrModuleError.Material_not_enough)
                return
            self.decItem(materialId, 1)

        self.putItemInBag(pieceID, card.strikeNeedCost)

        cardExp = int(card.exp * config["exp"])
        if cardExp > inHeriter.exp:
            inHeriter.exp = cardExp
            card.exp = 0
            card.level = 1
        mentalityLevelRate = config["mentalityLevel"]
        abilityRate = config["powerLevel"]

        # 意识属性传承
        self.InheritMentalityInfo(card, inHeriter, mentalityLevelRate)
        self.InheritAbilityInfo(card, inHeriter, abilityRate)

        # 等级配置
        levelConfig = levelIniConfig[0]
        # 最高等级
        maxLevel = levelConfig["maxLevel"]

        while (inHeriter.level <= maxLevel):
            # 等级最大
            if inHeriter.level == maxLevel:
                self.BallerCallBack(CardMgrModuleError.Baller_level_is_max)
                return

            levelUpgradeConfig = cardLevelUpgradeConfig[inHeriter.level]
            maxExp = levelUpgradeConfig["maxExp"]

            # 球员当前经验大于或等于所需升级经验，表示可以升到下一级，增加对应属性
            if inHeriter.exp >= maxExp:
                 inHeriter.level = inHeriter.level + 1
                 self.AddInfo(cardLevelUpgradeConfig[inHeriter.level], inHeriter)

            # 球员当前经验小于所需升级经验，不能继续升级，跳出循环
            elif inHeriter.exp < maxExp:
                 break
        card.calcFightValue()
        self.client.onInheritSucess(self.UpdateBallerInfo(inHeriter))

            # --------------------------------------------------------------------------------------------
            #                              工具函数调用函数
            # --------------------------------------------------------------------------------------------

    def UpdateBallerInfo(self,inHeriter):
        inHeriter.calcFightValue()
        playerInfo = {}
        playerInfo["id"] = inHeriter.id
        playerInfo["configID"] = inHeriter.configID
        playerInfo["star"] = inHeriter.star
        playerInfo["inTeam"] = inHeriter.inTeam
        playerInfo["bench"] = inHeriter.bench
        playerInfo["pos"] = inHeriter.pos
        playerInfo["isSelf"] = inHeriter.isSelf
        playerInfo["brokenLayer"] = inHeriter.brokenLayer
        playerInfo["fightValue"] = inHeriter.fightValue
        playerInfo["level"] = inHeriter.level
        playerInfo["exp"] = inHeriter.exp
        playerInfo["shoot"] = inHeriter.shoot
        playerInfo["shootM"] = inHeriter.shootM
        playerInfo["shootExp"] = inHeriter.shootExp
        playerInfo["defend"] = inHeriter.defend
        playerInfo["defendM"] = inHeriter.defendM
        playerInfo["defendExp"] = inHeriter.defendExp
        playerInfo["pass"] = inHeriter.passBall
        playerInfo["passBallM"] = inHeriter.passBallM
        playerInfo["passBallExp"] = inHeriter.passBallExp
        playerInfo["trick"] = inHeriter.trick
        playerInfo["trickM"] = inHeriter.trickM
        playerInfo["trickExp"] = inHeriter.trickExp
        playerInfo["reel"] = inHeriter.reel
        playerInfo["reelM"] = inHeriter.reelM
        playerInfo["reelExp"] = inHeriter.reelExp
        playerInfo["steal"] = inHeriter.steal
        playerInfo["stealM"] = inHeriter.stealM
        playerInfo["stealExp"] = inHeriter.stealExp
        playerInfo["controll"] = inHeriter.controll
        playerInfo["controllM"] = inHeriter.controllM
        playerInfo["controllExp"] = inHeriter.controllExp
        playerInfo["keep"] = inHeriter.keep
        playerInfo["keepM"] = inHeriter.keepM
        playerInfo["keepExp"] = inHeriter.keepExp
        playerInfo["tech"] = inHeriter.tech
        playerInfo["health"] = inHeriter.health
        playerInfo["strikeNeedCost"] = inHeriter.strikeNeedCost
        playerInfo["keepPercent"] = inHeriter.keepPercent
        playerInfo["controllPercent"] = inHeriter.controllPercent
        playerInfo["shootPercent"] = inHeriter.shootPercent
        playerInfo["defendPercent"] = inHeriter.defendPercent
        return playerInfo




    def BallerCallBack(self, errorID):
        self.client.onBallerCallBack(errorID)

    # 球员升级增加对应属性
    def AddInfo(self, levelUpgradeConfig, inHeriter):
        inHeriter.shoot = inHeriter.shoot + levelUpgradeConfig["shoot"]
        inHeriter.passBall = inHeriter.passBall + levelUpgradeConfig["pass"]
        inHeriter.reel = inHeriter.reel + levelUpgradeConfig["reel"]
        inHeriter.defend = inHeriter.defend + levelUpgradeConfig["defend"]
        inHeriter.trick = inHeriter.trick + levelUpgradeConfig["trick"]
        inHeriter.steal = inHeriter.steal + levelUpgradeConfig["steal"]
        inHeriter.controll = inHeriter.controll + levelUpgradeConfig["controll"]
        inHeriter.keep = inHeriter.keep + levelUpgradeConfig["keep"]

    # 球员继承意识属性
    def InheritMentalityInfo(self, carder, inHeriter, mentalityLevelRate):
        if carder.shootM * mentalityLevelRate > inHeriter.shootM:
            inHeriter.shootM = int(carder.shootM * mentalityLevelRate)
        carder.shootM = 0

        if carder.passBallM * mentalityLevelRate > inHeriter.passBallM:
            inHeriter.passBallM = int(carder.passBallM * mentalityLevelRate)
        carder.passBallM = 0

        if carder.reelM * mentalityLevelRate > inHeriter.reelM:
            inHeriter.reelM = int(carder.reelM * mentalityLevelRate)
        carder.reelM = 0

        if carder.defendM * mentalityLevelRate > inHeriter.defendM:
            inHeriter.defendM = int(carder.defendM * mentalityLevelRate)
        carder.defendM = 0

        if carder.trickM * mentalityLevelRate > inHeriter.trickM:
            inHeriter.trickM = int(carder.trickM * mentalityLevelRate)
        carder.trickM = 0

        if carder.stealM * mentalityLevelRate > inHeriter.stealM:
            inHeriter.stealM = int(carder.stealM * mentalityLevelRate)
        carder.stealM = 0

        if carder.controllM * mentalityLevelRate > inHeriter.controllM:
            inHeriter.controllM = int(carder.controllM * mentalityLevelRate)
        carder.controllM = 0

        if carder.keepM * mentalityLevelRate > inHeriter.keepM:
            inHeriter.keepM = int(carder.keepM * mentalityLevelRate)
        carder.controllM = 0

        # 球员继承能力属性
    def InheritAbilityInfo(self, carder, inHeriter, abilityRate):
        if carder.shootExp * abilityRate > inHeriter.shootExp:
            inHeriter.shootExp = int(carder.shootExp * abilityRate)
        carder.shootExp = 0

        if carder.passBallExp * abilityRate > inHeriter.passBallExp:
            inHeriter.passBallExp = int(carder.passBallExp * abilityRate)
        carder.passBallExp = 0

        if carder.reelExp * abilityRate > inHeriter.reelExp:
            inHeriter.reelExp = int(carder.reelExp * abilityRate)
        carder.reelExp = 0

        if carder.defendExp * abilityRate > inHeriter.defendExp:
            inHeriter.defendExp = int(carder.defendExp * abilityRate)
        carder.defendExp = 0

        if carder.trickExp * abilityRate > inHeriter.trickExp:
            inHeriter.trickExp = int(carder.trickExp * abilityRate)
        carder.trickExp = 0

        if carder.stealExp * abilityRate > inHeriter.stealExp:
            inHeriter.stealExp = int(carder.stealExp * abilityRate)
        carder.stealExp = 0

        if carder.controllExp * abilityRate > inHeriter.controllExp:
            inHeriter.controllExp = int(carder.controllExp * abilityRate)
        carder.controllExp = 0

        if carder.keepExp * abilityRate > inHeriter.keepExp:
            inHeriter.keepExp = int(carder.keepExp * abilityRate)
        carder.keepExp = 0
