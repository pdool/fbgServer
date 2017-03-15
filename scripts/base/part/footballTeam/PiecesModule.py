# -*- coding: utf-8 -*-


__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from ErrorCode import PieceCombineError
from KBEDebug import *
from itemsConfig import itemsIndex
from itemsPieces import itemsPiecesConfig

if __name__ == "__main__":
    print(__file__)
    pass

"""
碎片容器
"""
class PiecesModule:

    def __init__(self):
        # 球员碎片容器
        self.piecesContainer = {}

    def loadPiecesItem(self):
        colTupe= ("sm_UUID","sm_itemID","sm_amount")
        filterMap = {"sm_roleID":self.databaseID}
        sql = util.getSelectSql("tbl_ItemPieces",colTupe,filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("PiecesModule  loadPiecesItem")
            if result is None:
                return
            for i in range(len(result)):
                pieceItem = {}
                pieceItem[PieceItemKeys.uuid] = int(result[i][0])
                pieceItem[PieceItemKeys.itemID] = int(result[i][1])
                pieceItem[PieceItemKeys.amount] = int(result[i][2])
                self.piecesContainer[ pieceItem[PieceItemKeys.uuid]] = pieceItem

                if  pieceItem[PieceItemKeys.uuid] not in self.bagUUIDList:
                    self.bagUUIDList.append( pieceItem[PieceItemKeys.uuid])

        KBEngine.executeRawDatabaseCommand(sql,cb)
        pass


    # 增加碎片
    def addPieces(self,configID,count):
        # 1、是否可以合并
        togetherCount = 1
        pieceConfig = itemsIndex[configID]
        if pieceConfig["togetherCount"] != 0:
            togetherCount = pieceConfig["togetherCount"]

        if togetherCount <= 1:
            for i in range(count):
                self.__insertPieces(configID, count)
        else:
            self.__updatePieces(configID, count)
    # 减少碎片
    def decPieces(self,uuid,count):
        if uuid not in self.piecesContainer:
            self.client.onPieceError(PieceCombineError.Piece_not_exist)
            return False

        curCount = self.piecesContainer[uuid]["amount"]

        if curCount < count:
            self.client.onPieceError(PieceCombineError.Piece_not_enough)
            return False

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemPieces", setMap, filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.piecesContainer[uuid]["amount"] = curCount - count
                self.writeToDB()
                return  True

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemPieces",filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                del self.piecesContainer[uuid]
                self.bagUUIDList.remove(uuid)
                self.writeToDB()
                return  True

            KBEngine.executeRawDatabaseCommand(sql, cb)




    def __insertPieces(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemPieces",rowValueMap)

        @util.dbDeco
        def cb(result, rownum, error):
            del rowValueMap["roleID"]
            self.piecesContainer[rowValueMap["UUID"]] = rowValueMap
            self.bagUUIDList.append(rowValueMap["UUID"])
            self.writeToDB()


        KBEngine.executeRawDatabaseCommand(sql,cb)

        pass
    def __updatePieces(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.piecesContainer.values():
            if item["itemID"] != configID:
                continue
            isFind = True
            curCount = item["amount"]

            setMap = {"amount": curCount + addCount}
            filterMap = {"roleID":self.databaseID,"UUID":item["UUID"]}
            sql = util.getUpdateSql("tbl_ItemPieces",setMap,filterMap)

            @util.dbDeco
            def cb(result, rownum, error):
                self.piecesContainer[item["UUID"]]["amount"] = curCount + addCount
                self.writeToDB()

            KBEngine.executeRawDatabaseCommand(sql,cb)

        if isFind == True:
            return
        return self.__insertPieces(configID, addCount)


    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 合成
    def onClientCommbine(self,uuid):

        # 1、检查碎片是否存在
        # 2、修改数量
        # 3、修改背包
        # 4、生成球员
        if uuid not in self.piecesContainer:
            self.client.onPieceError(PieceCombineError.Piece_not_exist)

        pieceItem = self.piecesContainer[uuid]

        configID = pieceItem[PieceItemKeys.itemID]
        amount = pieceItem[PieceItemKeys.amount]

        needCount = itemsPiecesConfig[configID]["combineCount"]

        cardID =  itemsPiecesConfig[configID]["cardID"]

        if amount < needCount:
            self.client.onPieceError(PieceCombineError.Piece_not_enough)


        self.decPieces(uuid,needCount)
        def cb(player):
            ERROR_MSG("------------  card  info---------------")
            playerInfo = {}
            playerInfo["id"] = player.databaseID
            playerInfo["configID"] = player.configID
            playerInfo["level"] = player.level
            playerInfo["star"] = player.star
            playerInfo["exp"] = player.exp
            playerInfo["inTeam"] = player.inTeam
            playerInfo["isSelf"] = player.isSelf
            playerInfo["brokenLayer"] = player.brokenLayer
            playerInfo["fightValue"] = player.fightValue
            playerInfo["shoot"] = player.shoot
            playerInfo["shootM"] = player.shootM
            playerInfo["shootExp"] = player.shootExp
            playerInfo["defend"] = player.defend
            playerInfo["defendM"] = player.defendM
            playerInfo["defendExp"] = player.defendExp
            playerInfo["pass"] = player.passBall
            playerInfo["passBallM"] = player.passBallM
            playerInfo["passBallExp"] = player.passBallExp
            playerInfo["trick"] = player.trick
            playerInfo["trickM"] = player.trickM
            playerInfo["trickExp"] = player.trickExp
            playerInfo["reel"] = player.reel
            playerInfo["reelM"] = player.reelM
            playerInfo["reelExp"] = player.reelExp
            playerInfo["steal"] = player.steal
            playerInfo["stealM"] = player.stealM
            playerInfo["stealExp"] = player.stealExp
            playerInfo["controll"] = player.controll
            playerInfo["controllM"] = player.controllM
            playerInfo["controllExp"] = player.controllExp
            playerInfo["keep"] = player.keep
            playerInfo["keepM"] = player.keepM
            playerInfo["keepExp"] = player.keepExp
            playerInfo["tech"] = player.tech
            playerInfo["health"] = player.health
            playerInfo["strikeNeedCost"] = player.strikeNeedCost
            self.client.onCombineCardInfo(playerInfo)
        self.addCard(cardID,cb=cb)

        pass
    # 突破
    def onClientBroke(self,uuid):
        pass

    def onClientGetAllPieces(self):

        DEBUG_MSG("-------------onClientGetAllPieces-------------------------------")
        # vs = self.piecesContainer.values()
        #
        # for v1 in vs:
        #     for k,v in v1.items():
        #         ERROR_MSG("  k " + str(k) + "  v   " + str(v))
        #     break
        # ERROR_MSG(" kkkkkkkkkkkkkkkkkk              " + str( type(self.piecesContainer.values())))
        self.client.onGetAllPieces(list(self.piecesContainer.values()))
        pass

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------



class PieceItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
