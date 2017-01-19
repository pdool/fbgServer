# -*- coding: utf-8 -*-
import KBEngine

__author__ = 'chongxin'
from KBEDebug import DEBUG_MSG


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

    def destroySelf( self ):
        self.destroy()

class EquipPos:

    head = "head"
    body = "body"
    hand = "hand"
    leg = "leg"
    foot = "foot"

class CardStatus:
    on = 1
    out =2