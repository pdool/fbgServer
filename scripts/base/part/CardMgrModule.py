# -*- coding: utf-8 -*-
from cardsConfig import cardsConfig

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *

class PlayerInfoSelfStatus:
    notSelf = 0
    isSelf = 1

class CardMgrModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        self.cardIDList = []  # 玩家拥有的卡牌对象内存ID

        for cardDBID in self.cardDBIDList:
            KBEngine.createBaseFromDBID("Card", cardDBID, self.loadCardCB)
        pass

    """
    baseRef会是一个mailbox或者是新创建的Base实体的直接引用
    dbid会是实体的数据库ID
    wasActive是True则baseRef是已经存在的实体的引用(已经从数据库检出)
    """
    def loadCardCB(self, baseRef, dbid, wasActive):
        if wasActive:
            ERROR_MSG("player :(%i):not create success!" % (self.id))
            return
        if baseRef is None:
            ERROR_MSG("player is not exist")
            return

        card = KBEngine.entities.get(baseRef.id)
        if card is None:
            ERROR_MSG("player create fail")
            return
        if card.isSelf == 1:
            self.cardID = card.id
        self.cardIDList.append(card.id)


        pass
    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def onClientGetAllCardInfo(self):
        DEBUG_MSG("-----------------onClientGetAllCardInfo 1-------------------------------------")
        playerInfos = []
        for id in self.cardIDList:
            player = KBEngine.entities.get(id)

            playerInfo = {}
            playerInfo["DBID"] = player.databaseID
            playerInfo["configID"] = player.configID
            playerInfo["level"] = player.level
            playerInfo["star"] = player.star
            playerInfo["exp"] = player.exp
            playerInfo["inTeam"] = player.inTeam
            playerInfo["isSelf"] = player.isSelf

            playerInfos.append(playerInfo)


        DEBUG_MSG("-----------------onClientGetAllCardInfo 2-------------------------------------")
        self.client.onGetAllCardInfo(playerInfos)





    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def addCard(self,configID,isSelf = PlayerInfoSelfStatus.notSelf):

        if configID not in cardsConfig:
            return

        config = cardsConfig[configID]

        card = KBEngine.createBaseLocally("Card")

        if card is not None:
            card.roleID = self.databaseID
            card.configID = config["id"]
            card.isSelf =isSelf
            card.shoot = config["shoot"]
            card.defend =  config["defend"]
            card.passBall = config["pass"]
            card.trick = config["trick"]
            card.reel = config["reel"]
            card.controll = config["controll"]
            card.keep = config["keep"]
            card.inTeam = PlayerInfoTeamStatus.notInTeam

            card.writeToDB(self.__onCardSaved)
        else:
            DEBUG_MSG("card is not None")

    def __onCardSaved(self, success, card):

        if self.isDestroyed:
            if card is not None:
                card.destroy(True)

        DEBUG_MSG("----------------------------------------")
        self.cardDBIDList.append(card.databaseID)
        self.writeToDB()
        self.cardIDList.append(card.id)


class PlayerInfoKeys:
    configID = "configID"
    level = "level"
    star = "star"
    exp = "exp"
    inTeam = "inTeam"



class PlayerInfoTeamStatus:
    notInTeam = 0
    inTeam = 1

