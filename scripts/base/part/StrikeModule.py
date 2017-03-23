# -*- coding: utf-8 -*-
import TimerDefine
import util
from KBEDebug import *
import strikeConfig
import CardByColor
from ErrorCode import CardMgrModuleError
import shopConfig

__author__ = 'yanghao'

if __name__ == "__main__":
    useStr={102019: 15,102020: 3}
    print(useStr.split(','))
    pass
# 突破模块
class StrikeModule:
    def __init__(self):
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    def StrikeBaller(self, cardId, ItemId):
        if cardId not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        self.itemId = ItemId
        card = KBEngine.entities.get(cardId)
        if card.brokenLayer >= 20:
            self.client.onBallerCallBack(CardMgrModuleError.Strike_is_max)
            return
        strikeID = card.star * 100 + card.brokenLayer + 1


        Config = strikeConfig.StrikeConfig[strikeID]

        ERROR_MSG("strikeID  " + str(strikeID) + "  needCount " + str(Config["needCount"]))
        itemCount = self.getItemNumByItemID(ItemId)
        ERROR_MSG(" ===========StrikeBaller====ItemId  " + str(ItemId)  + "   count  "+ str(itemCount))
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


    def SwitchPiece(self, ItemId, pieceId, number, cardID):
        if cardID not in self.cardIDList:
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return
        itemCount = self.getItemNumByItemID(pieceId)
        if itemCount < number:
            self.client.onBallerCallBack(CardMgrModuleError.Material_not_enough)
            return
        card = KBEngine.entities.get(cardID)
        config = CardByColor.UsePieces[card.star]
        money = config["money"]
        if self.euro >= money * number:
            self.euro = self.euro - money * number
            self.decItem(pieceId, number)
            self.putItemInBag(ItemId, number)
            self.client.onBallerCallBack(CardMgrModuleError.Switch_is_sucess)
        else:
            self.client.onBallerCallBack(CardMgrModuleError.Money_not_enough)
            return


            # --------------------------------------------------------------------------------------------
            #                              工具函数调用函数
            # --------------------------------------------------------------------------------------------



