# -*- coding: utf-8 -*-
import KBEngine
import propChangeFightConfig
from KBEDebug import ERROR_MSG
import math
__author__ = 'chongxin'

"""
单张卡牌
"""

class Card(KBEngine.Base):
    def __init__(self):
        pass
        #
        # self.playerID = 0               # 配置ID
        # self.level = 0                  # 等级
        # self.exp = 0                    # 经验
        # self.star = 0                   # 星级
        # self.brokenLayer = 0            # 突破层级
        # self.fightValue = 0             # 战斗力
        # self.shoot = 0                  # 射门
        # self.defend = 0                 # 防守
        # self.passBall  = 0              # 传球
        # self.trick = 0                  # 拦截
        # self.reel = 0                   # 盘带
        # self.steal = 0                  # 抢断
        # self.controll = 0               # 控球
        # self.keep = 0                   # 守门
        # self.tech = 0                   # 技术
        # self.health = 0                 # 身体
        # self.inPlay = 0    # 出场
        # self.equips = {}                # 装备
        #
        # DEBUG_MSG("------------Player-----init-------------------------")


    def __initProp__(self,configId):
        pass

    def destroyCard( self ):
        if self.cell is not None:
        # 销毁cell实体
            self.destroyCellEntity()
            self.cellLoseReason = "clientDeath"
            return
        self.destroy()
    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        if hasattr(self, "cellLoseReason"):
            ERROR_MSG("cellLoseReason   is " + self.cellLoseReason)



        if hasattr(self,"cellLoseReason") and self.cellLoseReason == "clientDeath":
            self.destroy()
    def destroyCardCell( self ):
        if self.cell is not None:
        # 销毁cell实体

            # ERROR_MSG("      destroyCardCell        " + str(self.id))


            self.destroyCellEntity()


    # 计算战斗力
    """
    属性战力计算方法=int（射门值*射门战力系数+传球值*传球战力系数+盘带值*盘带战力系数+……+守门值*守门战力系数）
                    战力系数
        1射门	=	1.2战力
        1传球	=	0.6战力
        1盘带	=	0.6战力
        1%技术	=	800战力
        1控球	=	0.4战力
        1防守	=	2.4战力
        1拦截	=	0.6战力
        1抢断	=	0.6战力
        1%身体	=	800战力
        1守门	=	1.5战力
    """
    def calcFightValue(self):
        avatar = KBEngine.entities.get(self.playerID)
        oldFightValue = self.fightValue

        shoot       = self.shoot  * 1.2
        passBall    = self.passBall * 0.6
        reel        = self.reel * 0.6
        tech        = self.tech * 800
        controll    = self.controll * 0.4
        defend      = self.defend * 2.4
        trick       = self.trick * 0.6
        steal       = self.steal *0.6
        health      = self.health * 800
        keep        = self.keep * 1.5



        formationFight = self.formationValue()
        fightValue = math.ceil(shoot + passBall + reel + tech + controll + defend + trick + steal + health + keep + formationFight)
        self.fightValue = fightValue

        if self.inTeam == 1:
            if oldFightValue != fightValue:
                avatar.fightValue = avatar.fightValue - oldFightValue + fightValue


        avatar.client.onCardFightValueChange(self.id,fightValue)
        avatar.updateFightValueRank()
        card = KBEngine.entities.get(self.id)
        if card is None:
            return
        if card.isSelf != 1:
            avatar.updateBallerValueRank(card)
        return  fightValue

    # 减去下阵球员战斗力
    def subBallerFightValue(self):
        avatar = KBEngine.entities.get(self.playerID)
        avatar.fightValue = avatar.fightValue - self.fightValue

        pass

    # 增加上阵球员战斗力
    def addBallerFightValue(self):
        avatar = KBEngine.entities.get(self.playerID)
        avatar.fightValue = avatar.fightValue + self.fightValue

    # 阵型战斗力
    def formationValue(self):

        avatar = KBEngine.entities.get(self.playerID)


        if self.id not in  avatar.inTeamcardIDList :
            return 0

        fightValue = 0

        propChangeFight = propChangeFightConfig.PropChangeFightConfig[1]

        # 阵型加成
        for id in avatar.fomationPropContainer:
            formatList = avatar.fomationPropContainer[id]
            for info in formatList:
                name = info["propName"]
                value = info["value"]
                # ERROR_MSG("--FormatName--" + str(name) + "--Formatvalue--" + str(value))
                fightValue = fightValue + int(propChangeFight[name] * value)

        # ERROR_MSG("-- formatFightAdd--" + str(fightValue)+"--avatar.relatPropContainer--"+str(len(avatar.relatPropContainer)))

        # 羁绊球员属性加成
        if self.id not in avatar.relatPropContainer:
            return fightValue

        relatePropList = avatar.relatPropContainer[self.id]

        relatefightAdd = 0
        for propInfo in relatePropList:
            name = propInfo["propName"]
            value =  propInfo["value"]
            ERROR_MSG("--propName--" + str(name)+"--propvalue--" +str(value))
            fightValue = fightValue+int(propChangeFight[name]*value)
            relatefightAdd = relatefightAdd + int(propChangeFight[name]*value)
        # ERROR_MSG("--relatefightAdd--"+str(relatefightAdd))

        return fightValue





class EquipPos:

    head = "head"
    body = "body"
    hand = "hand"
    leg = "leg"
    foot = "foot"

class CardStatus:
    on = 1
    out =2