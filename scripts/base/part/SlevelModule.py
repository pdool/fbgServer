# -*- coding: utf-8 -*-
import KBEngine
from ErrorCode import CardMgrModuleError
import upStar
import cardsConfig
# 不需要使用def,继承就可以使用，def可以用来生成数据库的表
# 如何使用回调
import sys

__author__ = 'yanghao'


class SlevelModule:
    def __init__(self):
        pass

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    def onClientUpStar(self, cardId):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)

        maxStar = cardsConfig.cardsConfig[card.configID]["maxStar"]

        if card.star == maxStar:
            self.client.onBallerCallBack(CardMgrModuleError.Card_is_max_level)
            return

        config = upStar.UpStarConfig[card.star]
        cost_info = config["useStr"]
        for itemId, num in cost_info.items():
            have = self.getItemNumByItemID(itemId)
            if have < num:
                self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
                return

        for itemId, num in cost_info.items():
            self.decItem(itemId, num)
            # if self.decItem(itemId, num) is False:
            #     return

        card.star = card.star + 1
        card.shoot = card.shoot + config["shoot"]
        card.defend = card.defend + config["defend"]
        card.passBall = card.passBall + config["pass"]
        card.trick = card.trick + config["trick"]
        card.reel = card.reel + config["reel"]
        card.steal = card.steal + config["steal"]
        card.controll = card.controll + config["controll"]
        card.keep = card.keep + config["keep"]
        card.health = card.health + config["health"]
        card.tech = card.tech + config["tech"]

        self.client.onBallerCallBack(CardMgrModuleError.Slevel_sucess)

        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------
