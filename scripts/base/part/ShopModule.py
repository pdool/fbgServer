# -*- coding: utf-8 -*-
import TimerDefine
import util
import vipConfig
from KBEDebug import *

import shopConfig

__author__ = 'chongxin'

Shop_type_month = 0
Shop_type_season = 1
Shop_type_common = 2

Shop_month_id = 1
Shop_season_id = 2

# 商城

class ShopModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        rebateTime = shopConfig.baseConfig[1]["rebateTime"]
        offset = util.getLeftSecsToNextHMS(rebateTime,0,0)
        self.addTimer( offset, 24 * 60 * 60, TimerDefine.Timer_shop_recover)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def onClientCharge(self,cardId):

        config = shopConfig.cardConfig[cardId]
        cardType = config["goodsType"]
        if cardType == Shop_type_month:
            self.getMonthCard(config)
        elif cardType == Shop_type_season:
            self.getSeasonCard(config)
        elif cardType == Shop_type_common:
            self.getCommonCard(config)

    # 领取vip礼包
    def onClientGetVipGift(self):






        pass
    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------
    def getMonthCard(self,config):
        diamondCount = config["diamondCount"]
        rmbPrice = config["rmbPrice"]
        giveDiamond = config["giveDiamond"]
        rebateTimes = config["rebateTimes"]

        self.diamond = self.diamondCount + diamondCount + giveDiamond
        self.addRmb(rmbPrice)
        self.monthRebateTimes = self.monthRebateTimes + rebateTimes




    def getSeasonCard(self, config):
        diamondCount = config["diamondCount"]
        rmbPrice = config["rmbPrice"]
        giveDiamond = config["giveDiamond"]
        rebateTimes = config["rebateTimes"]

        self.diamond = self.diamond + diamondCount + giveDiamond
        self.addRmb(rmbPrice)
        self.seasonRebateTimes = self.seasonRebateTimes + rebateTimes

    def getCommonCard(self, config):
        cardId = config["id"]
        diamondCount =config["diamondCount"]
        rmbPrice = config["rmbPrice"]
        giveDiamond = config["giveDiamond"]
        firstBuyGive =config["firstBuyGive"]

        firstBuySet = set(self.firstBuyInfo)

        self.addRmb(rmbPrice)
        self.diamond = self.diamond + diamondCount + giveDiamond

        if cardId not in firstBuySet:
        #     是第一次购买
            self.diamond = self.diamond + firstBuyGive
            self.firstBuyInfo.append(cardId)
            self.writeToDB()


    def onTimer(self, tid, userArg):

        if userArg != TimerDefine.Timer_shop_recover:
            return
        DEBUG_MSG("------------------------ run time")
        DEBUG_MSG("---------------------------" + str(type(self)))
        if self.monthRebateTimes > 0:
            config = shopConfig.cardConfig[Shop_month_id]
            self.diamond = self.diamond + config["rebateCount"]
            self.monthRebateTimes = self.monthRebateTimes -1


        if self.seasonRebateTimes > 0:
            config = shopConfig.cardConfig[Shop_season_id]
            self.diamond = self.diamond + config["rebateCount"]
            self.seasonRebateTimes = self.seasonRebateTimes - 1



    def addRmb(self,num):
        self.rmb = self.rmb + num
        vip = self.vipLevel
        for i in range(self.vipLevel + 1,16):
            config = vipConfig.VipConfig[i]
            needRmb= config["rmbNum"]
            if self.rmb >= needRmb:
                vip = i
            else:
                break
        if vip != self.vipLevel:
            self.vipLevel = vip


if __name__ == "__main__":

    s = ShopModule()
    s.rmb = 0
    s.vipLevel = 0
    s.addRmb(1000)
    print(s.vipLevel)
    s.addRmb(1000)
    print(s.vipLevel)



























