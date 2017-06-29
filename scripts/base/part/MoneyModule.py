# -*- coding: utf-8 -*-
from ErrorCode import GameShopModuleError
from part.GameShopModule import GuildDonate_type, BlackMoney_type, Euro_type, Diamond_type

__author__ = 'yangh'
"""
充钱花钱
"""


class MoneyModule:
    def onEntitiesEnabled(self):
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 充值欧元
    def rechargeEuro(self, money):
        self.euro = self.euro + money
        self.updateMoneyValueRank()

    # 消耗欧元
    def useEuro(self, money):
        self.euro = self.euro - money
        self.updateMoneyValueRank()





        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------

    def delMoneyByType(self, type, money):
        if type == Diamond_type:
            if self.diamond < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Diamod_not_enough)
                return False
            self.diamond = self.diamond - money
        elif type == Euro_type:
            if self.euro < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Euro_not_enough)
                return False
            self.useEuro(money)
        elif type == BlackMoney_type:
            if self.blackMoney < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Black_not_enough)
                return False
            self.blackMoney = self.blackMoney - money
        elif type == GuildDonate_type:
            if self.guildDonate < money:
                self.client.onShopInfoCallBack(GameShopModuleError.Guild_not_enough)
                return False
            self.guildDonate = self.guildDonate - money
        return True
