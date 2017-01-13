# -*- coding: utf-8 -*-


__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

import util
from KBEDebug import *
from ErrorCode import PieceCombineError
from itemsPieces import itemsPiecesConfig
from itemsConfig import itemsIndex
from part.BagModule import ItemTypeEnum

if __name__ == "__main__":
    print(__file__)
    pass
"""
碎片合成模块
"""
class PiecesModule:

    def __init__(self):
        # 球员碎片容器
        self.piecesContainer = {}

    def loadPiecesItem(self):
        colTupe= ("sm_UUID","sm_itemID","sm_amount")
        filterMap = {"sm_roleID":self.databaseID}
        sql = util.getSelectSql("tbl_ItemPieces",colTupe,filterMap)

        def cb(result, rownum, error):
            DEBUG_MSG("PiecesModule  loadPiecesItem")
            if result is None:
                return

            for i in range(len(result)):
                pieceItem = {}
                pieceItem[PieceItemKeys.uuid] = int(result[i][0])
                pieceItem[PieceItemKeys.itemID] = int(result[i][1])
                pieceItem[PieceItemKeys.amount] = int(result[i][2])
                pieceItem[PieceItemKeys.itemType] = ItemTypeEnum.Pieces
                self.piecesContainer[ pieceItem[PieceItemKeys.uuid]] = pieceItem


        KBEngine.executeRawDatabaseCommand(sql,cb)
        pass


    # 增加碎片
    def addPieces(self,configID,count):
        # 1、是否可以合并
        togetherCount = 1
        pieceConfig = itemsIndex[configID]
        if pieceConfig["togetherCount"] != 0:
            togetherCount = pieceConfig["togetherCount"]

        if togetherCount == 1:
            self.__insertPieces(configID, count)
        else:
            self.__updatePieces(configID, count)
    # 减少碎片
    def decPieces(self,uuid,count):
        if uuid not in self.piecesContainer:
            self.onPieceError(PieceCombineError.Piece_not_exist)
            return

        curCount = self.piecesContainer[uuid]["amount"]

        if curCount < count:
            self.onPieceError(PieceCombineError.Piece_not_enough)
            return

        if curCount > count:
            setMap = {"amount": curCount - count}
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getUpdateSql("tbl_ItemPieces", setMap, filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return
                self.piecesContainer[uuid]["amount"] = curCount - count

            KBEngine.executeRawDatabaseCommand(sql, cb)
        elif curCount == count:
            filterMap = {"roleID": self.databaseID, "UUID": uuid}
            sql = util.getDelSql("tbl_ItemPieces",filterMap)

            def cb(result, rownum, error):
                if error is not None:
                    return False
                del self.piecesContainer[uuid]
                self.bagUUIDList.remove(uuid)
                self.writeToDB()

            KBEngine.executeRawDatabaseCommand(sql, cb)




    def __insertPieces(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count

        sql = util.getInsertSql("tbl_ItemPieces",rowValueMap)

        def cb(result, rownum, error):
            if rownum != 1:
                self.client.onPieceError(1)
            else:
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

            def cb(result, rownum, error):
                self.piecesContainer[item["UUID"]]["amount"] = curCount + addCount

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
            self.onPieceError(PieceCombineError.Piece_not_exist)

        pieceItem = self.piecesContainer[uuid]

        configID = pieceItem[PieceItemKeys.itemID]
        amount = pieceItem[PieceItemKeys.amount]

        needCount = itemsPiecesConfig[configID]["combineCount"]

        cardID =  itemsPiecesConfig[configID]["cardID"]

        if amount < needCount:
            self.onPieceError(PieceCombineError.Piece_not_enough)


        self.decPieces(uuid,needCount)

        self.addCard(cardID)

        pass

    # 突破
    def onClientBroke(self,uuid):
        pass


    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------



class PieceItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemType = "itemType"
