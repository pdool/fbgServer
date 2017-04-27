# -*- coding: utf-8 -*-
import KBEngine
import ClothesConfig
import ClothesLevelConfig
import ClothesSlevelConfig
import CommonConfig
import TimerDefine
from ErrorCode import CardMgrModuleError
import BabyLikingStarConfig
from KBEDebug import ERROR_MSG
import util

"""
足球宝贝 yanghao write
"""


class Baby(KBEngine.Base):
    def __init__(self):

        config = CommonConfig.CommonConfig[4]
        time = config["value"]
        if util.getCurrentTime() - self.fullTime <= 6 * 60 * 60 and util.getCurrentTime() - self.fullTime > 0:
            self.addTimer(6 * 60 * 60 - (util.getCurrentTime() - self.fullTime), time * 60,
                          TimerDefine.Timer_reset_baby_fullTime)
            return
        if self.isFullTime == 1:
            period = self.periodTime - 6 * 60 * 60
            self.isFullTime = 0
        else:
            currentTime = util.getCurrentTime()
            period = currentTime - self.periodTime
        index = period // (time * 60)
        lastTime = period % (time * 60)
        configs = CommonConfig.CommonConfig[5]
        if index > 0:
            liking = configs["value"] * index
            if self.liking >= liking:
                self.liking = self.liking - liking
            else:
                self.liking = 0
            if self.liking == 0:
                self.likingTime = 0
                return
            else:
                minute = self.liking // configs["value"]
                second = minute * time * 60 - lastTime
                self.likingTime = second
        else:
            minute = self.liking // configs["value"]
            if minute == 0:
                return
            if self.likingTime > 0:
                self.likingTime = self.likingTime - lastTime
            else:
                self.likingTime = minute * time * 60 - lastTime

        tech = 0.0
        health = 0.0
        for i in range(5):
            info = BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["liking"]
            tech = tech + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[1])
            health = health + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[0])
            if self.liking <= info:
                break
        avatar = KBEngine.entities.get(self.playerID)
        player = KBEngine.entities.get(avatar.cardID)
        if player.tech != tech or player.health != health:
            player.tech = tech
            player.health = health
            self.client.onUpdateCardInfo(self.UpdateBallerInfo(player))

        self.addTimer(self.likingTime % (time * 60), time * 60, TimerDefine.Timer_reset_baby_liking)
        self.addTimer(1, 1, TimerDefine.Timer_reset_baby_likingTime)
        pass

    def onTimer(self, id, userArg):
        if userArg == TimerDefine.Timer_reset_baby_liking:
            config = CommonConfig.CommonConfig[5]
            liking = config["value"]
            if self.liking >= liking:
                self.liking = self.liking - liking
            else:
                self.liking = 0
                self.likingTime = 0
            self.client.onGetBabyInfo(self.liking, self.fullTime, self.closeTouch, self.itemTouch, self.likingTime,
                                      self.GetRewardList)
            tech = 0.0
            health = 0.0
            for i in range(5):
                info = BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["liking"]
                tech = tech + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[1])
                health = health + float(BabyLikingStarConfig.BabyLikingStarConfig[i + 1]["teamTuple"].split(",")[0])
                if self.liking <= info:
                    break
            avatar = KBEngine.entities.get(self.playerID)
            player = KBEngine.entities.get(avatar.cardID)
            if player.tech != tech or player.health != health:
                player.tech = tech
                player.health = health
                self.client.onUpdateCardInfo(self.UpdateBallerInfo(player))
        else:
            if self.likingTime > 0:
                self.likingTime = self.likingTime - 1
            else:
                self.likingTime = 0

    def destroyBaby(self):
        if util.getCurrentTime() - self.fullTime > 6 * 60 * 60:
            self.periodTime = util.getCurrentTime()
        self.delTimer(TimerDefine.Timer_reset_baby_liking)
        self.delTimer(TimerDefine.Timer_reset_baby_likingTime)
        self.destroy()

    def putItemInfoInBaby(self, suitID, buy):
        for i in range(5):
            itemInfo = {}
            clothesId = suitID * 10000 + i * 1000
            Config = ClothesConfig.ClothesConfig[clothesId]
            itemInfo["configID"] = clothesId
            itemInfo["type"] = Config["type"]
            itemInfo["isWear"] = buy
            itemInfo["level"] = 1
            itemInfo["star"] = Config["initStar"]
            itemInfo["exp"] = 0
            itemInfo["firstName"] = Config["firstName"]
            itemInfo["seondName"] = Config["seondName"]
            itemInfo["maxLevel"] = Config["maxLevel"]
            itemInfo["maxStar"] = Config["maxStar"]
            if itemInfo["isWear"] == 1:
                avatar = KBEngine.entities.get(self.playerID)
                if avatar.cardID not in avatar.cardIDList:
                    avatar.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
                    return
                levelId = clothesId + itemInfo["level"]
                levelConfig = ClothesLevelConfig.ClothesLevelConfig[levelId]
                slevelID = clothesId + Config["initStar"]
                slevelConfig = ClothesSlevelConfig.ClothesSlevelConfig[slevelID]
                name = Config["firstName"]
                addvalue = avatar.GetObjectValue(avatar.cardID, name) + levelConfig["firstValue"]
                addvalue = addvalue + slevelConfig["addvalue"]
                avatar.SetObjectValue(avatar.cardID, name, addvalue)
                card = KBEngine.entities.get(avatar.cardID)
                card.calcFightValue()
            self.itemList.append(itemInfo)
