# -*- coding: utf-8 -*-


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

        # 装备
