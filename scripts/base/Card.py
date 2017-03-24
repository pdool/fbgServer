# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import ERROR_MSG

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
        if hasattr(self,"cellLoseReason") and self.cellLoseReason == "clientDeath":
            self.destroy()
    def destroyCardCell( self ):
        if self.cell is not None:
        # 销毁cell实体
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

        string = "shoot   " + str(self.shoot) + "  passball " + str(self.passBall) +" reel " + str(self.reel)
        string = string + " tech " + str(self.tech) +" controll " + str(self.controll) + " defend "+ str(self.defend)
        string = string + " trick " + str(self.trick) + " steal " + str(self.steal) + " health " + str(self.health)
        string = string + " keep " + str(self.keep)

        # ERROR_MSG(string)
        fightValue = int(shoot + passBall + reel + tech + controll + defend + trick + steal + health + keep)

        self.fightValue = fightValue

        avatar.fightValue = avatar.fightValue - oldFightValue + fightValue

        avatar.client.onCardFightValueChange(self.id,fightValue)

        return  fightValue







class EquipPos:

    head = "head"
    body = "body"
    hand = "hand"
    leg = "leg"
    foot = "foot"

class CardStatus:
    on = 1
    out =2