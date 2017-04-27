# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *
import strikeConfig
import CardByColor
from ErrorCode import CardMgrModuleError
import shopConfig
import cardsConfig

__author__ = 'yanghao'


# 突破模块
class StrikeModule:
    def __init__(self):
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def StrikeBaller(self, cardId, ItemId):
        if cardId not in self.cardIDList:
            ERROR_MSG("       cardID       " + str(cardId))
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        self.itemId = ItemId
        card = KBEngine.entities.get(cardId)
        if card.brokenLayer >= 20:
            self.client.onBallerCallBack(CardMgrModuleError.Strike_is_max)
            return
        initStar = cardsConfig.cardsConfig[card.configID]["initStar"]
        strikeID = initStar * 100 + card.brokenLayer + 1


        Config = strikeConfig.StrikeConfig[strikeID]


        itemCount = self.getItemNumByItemID(ItemId)

        if itemCount < Config["needCount"]:
            self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
            return

        self.decItem(ItemId, Config["needCount"])
        card.brokenLayer = card.brokenLayer + 1
        card.shoot = card.shoot + Config["shoot"]
        card.defend = card.defend + Config["defend"]
        card.passBall = card.passBall + Config["pass"]
        card.trick = card.trick + Config["trick"]
        card.reel = card.reel + Config["reel"]
        card.steal = card.steal + Config["steal"]
        card.controll = card.controll + Config["controll"]
        card.keep = card.keep + Config["keep"]
        card.tech = card.tech + Config["tech"]
        card.health = card.health + Config["health"]
        card.strikeNeedCost = card.strikeNeedCost + Config["needCount"]
        self.client.onBallerCallBack(CardMgrModuleError.Strike_sucess)
        self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))



    def SwitchPiece(self, ItemId, pieceId, number, cardID):
        if cardID not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        itemCount = self.getItemNumByItemID(pieceId)
        if itemCount < number:
            self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
            return
        card = KBEngine.entities.get(cardID)
        initStar = cardsConfig.cardsConfig[card.configID]["initStar"]
        config = CardByColor.UsePieces[initStar]
        money = config["money"]
        if self.euro >= money * number:
            self.useEuro(money * number)
            self.decItem(pieceId, number)
            self.putItemInBag(ItemId, number)
            self.client.onBallerCallBack(CardMgrModuleError.Switch_is_sucess)
        else:
            self.client.onBallerCallBack(CardMgrModuleError.Money_not_enough)
            return


            # --------------------------------------------------------------------------------------------
            #                              工具函数调用函数
            # --------------------------------------------------------------------------------------------



