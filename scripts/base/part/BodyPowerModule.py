# -*- coding: utf-8 -*-
import TimerDefine
import bodyPowerConfig
import util
from ErrorCode import BodyPowerEroor
from KBEDebug import DEBUG_MSG

__author__ = 'chongxin'

"""
    体力模块
"""

class BodyPowerModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        resetBuyTime = bodyPowerConfig.bodyPowerConfig[1]["resetBuyTime"]
        resetBuyTimeOffset = util.getLeftSecsToNextHMS(resetBuyTime, 0, 0)
        self.addTimer(resetBuyTimeOffset, 24 * 60 * 60, TimerDefine.Timer_body_power_reset_buy_times)
        # 定时恢复心跳
        recoverTime = bodyPowerConfig.bodyPowerConfig[1]["recoverTime"] *60
        self.addTimer(recoverTime, recoverTime, TimerDefine.Timer_body_power_recover)
        # 下线时间体力恢复

        self.onOfflineRecoverPower()


        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def onClientBuyPower(self,num):

        if self.bodyPowerBuyTimes + num > bodyPowerConfig.bodyPowerConfig[1]["maxBuyTimes"]:
            # 没有购买次数
            self.client.onBodyPowerError(BodyPowerEroor.has_not_enough_buy_times)
            return
        needMoney = bodyPowerConfig.bodyPowerConfig[1]["singleBuyPowerNeedMoney"]

        if needMoney > self.diamond:
            # 没有足够的钱
            self.client.onBodyPowerError(BodyPowerEroor.has_not_enough_diamond)
            return

        buyPower = bodyPowerConfig.bodyPowerConfig[1]["singleBuyPowerNum"]
        powerLimit =  bodyPowerConfig.bodyPowerConfig[1]["powerLimit"]

        power = self.bodyPower + buyPower * num

        if power > powerLimit:
            power = powerLimit

        # 1、扣钱
        self.diamond = self.diamond - needMoney

        # 2、扣除购买次数
        self.bodyPowerBuyTimes = self.bodyPowerBuyTimes + num

        # 3、增加体力
        self.bodyPower = power



    # --------------------------------------------------------------------------------------------
    #                              服务器内部函数调用函数
    # --------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------


    def onTimer(self, tid, userArg):

        if userArg == TimerDefine.Timer_body_power_reset_buy_times:
            self.bodyPowerBuyTimes = 0

        # 每N分钟体力恢复1点
        if TimerDefine.Timer_body_power_recover == userArg:

            if self.bodyPower < bodyPowerConfig.bodyPowerConfig[1]["maxPower"]:

                DEBUG_MSG("----------------  Timer_body_power_recover  -----------------------")
                self.bodyPower = self.bodyPower + 1

        pass


    def onOfflineRecoverPower(self):

        current = util.getCurrentTime()
        logout = self.logoutTime
        recoverTime = bodyPowerConfig.bodyPowerConfig[1]["recoverTime"] * 60
        addPower = (current - logout)//recoverTime
        maxPower = bodyPowerConfig.bodyPowerConfig[1]["maxPower"]

        power = self.bodyPower + addPower
        if power <= maxPower:
            self.bodyPower = power
        else:
            self.bodyPower = maxPower























