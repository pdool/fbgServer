# -*- coding: utf-8 -*-
import TimerDefine
from ErrorCode import PieceCombineError
import util
from KBEDebug import *
from itemsConfig import itemsIndex
from itemsPieces import itemsPiecesConfig

__author__ = 'chongxin'
__createTime__  = '2017年1月5日'

"""
碎片容器
"""
class PiecesContainer:

    def __init__(self):
        # 碎片容器
        self.piecesContainer = {}
    def loadPieces(self):

        colTupe = ("sm_UUID", "sm_itemID","sm_amount")
        filterMap = {"sm_roleID": self.databaseID}
        sql = util.getSelectSql("tbl_ItemPieces", colTupe, filterMap)

        @util.dbDeco
        def cb(result, rownum, error):
            DEBUG_MSG("PiecesModule  loadPieces")
            if result is None:
                return
            for i in range(len(result)):
                item = {}
                uuid = int(result[i][0])
                item[PiecesItemKeys.uuid] = uuid
                item[PiecesItemKeys.itemID] = int(result[i][1])
                item[PiecesItemKeys.amount] = int(result[i][2])
                item[PiecesItemKeys.itemState] = DBState.NoAction

                self.piecesContainer[item[PiecesItemKeys.uuid]] = item

                if uuid not in self.bagUUIDList:
                    self.bagUUIDList.append(uuid)

        KBEngine.executeRawDatabaseCommand(sql, cb)

        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------
    # 合成
    def onClientCommbine(self, uuid):

        # 1、检查碎片是否存在
        # 2、修改数量
        # 3、修改背包
        # 4、生成球员
        if uuid not in self.piecesContainer:
            self.client.onPieceError(PieceCombineError.Piece_not_exist)

        pieceItem = self.piecesContainer[uuid]

        configID = pieceItem[PiecesItemKeys.itemID]
        amount = pieceItem[PiecesItemKeys.amount]

        needCount = itemsPiecesConfig[configID]["combineCount"]

        cardID = itemsPiecesConfig[configID]["cardID"]

        if amount < needCount:
            self.client.onPieceError(PieceCombineError.Piece_not_enough)

        self.decPieces(uuid, needCount)

        def cb(player):
            ERROR_MSG("------------  card  info---------------")
            playerInfo = {}
            playerInfo["id"] = player.id
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
            playerInfo["keepPercent"] = player.keepPercent
            playerInfo["controllPercent"] = player.controllPercent
            playerInfo["shootPercent"] = player.shootPercent
            playerInfo["defendPercent"] = player.defendPercent
            playerInfo["bench"] = player.bench
            playerInfo["pos"] = player.pos
            self.client.onCombineCardInfo(playerInfo)
        self.addCard(cardID, cb=cb)

        pass

    # 突破
    def onClientBroke(self, uuid):
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
        pieces = []
        for v in self.piecesContainer.values():
            item ={}
            item["UUID"] = v["UUID"]
            item["itemID"] = v["itemID"]
            item["amount"] = v["amount"]

            pieces.append(item)

        self.client.onGetAllPieces(pieces)
        pass

    # --------------------------------------------------------------------------------------------
    #                              工具函数
    # --------------------------------------------------------------------------------------------
    # 增加宝石
    def addPieces(self,configID,count = 1):
        # 1、是否可以合并
        togetherCount = 1
        pieceConfig = itemsIndex[configID]
        if pieceConfig["togetherCount"] != 0:
            togetherCount = pieceConfig["togetherCount"]

        if togetherCount <= 1 :
            for i in range(count):
                self.__insertPieces(configID, 1)
            return True
        else:
            return self.__updatePieces(configID, count)
    # 减少宝石
    def decPieces(self,uuid,count):
        if uuid not in self.piecesContainer:
            self.client.onPiecesError(PieceCombineError.Piece_not_exist)
            return False
        ERROR_MSG("-----------decPieces---------uuid-----------" + str(uuid))
        curCount = self.piecesContainer[uuid]["amount"]
        itemID = self.piecesContainer[uuid]["itemID"]

        if curCount < count:
            self.client.onPiecesError(PieceCombineError.Pieces_not_enough)
            return False

        if curCount > count:
            self.piecesContainer[uuid]["amount"] = curCount - count
            if self.piecesContainer[uuid]["state"] != DBState.Insert:
                self.piecesContainer[uuid]["state"] = DBState.Update
            self.noticeClientBagUpdate(uuid, self.piecesContainer[uuid]["itemID"], curCount - count)
            return True

        elif curCount == count:
            oldState =  self.piecesContainer[uuid]["state"]
            if oldState == DBState.Insert:
                del self.piecesContainer[uuid]
            elif oldState == DBState.Update or oldState == DBState.NoAction:
                self.piecesContainer[uuid]["state"] = DBState.Del
            self.noticeClientBagUpdate(uuid, itemID, 0)
            return True




    def __insertPieces(self, configID, count = 1):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["UUID"] = KBEngine.genUUID64()
        rowValueMap["itemID"] = configID
        rowValueMap["amount"] = count
        rowValueMap["state"] = DBState.Insert
        self.piecesContainer[rowValueMap["UUID"]] = rowValueMap
        self.noticeClientBagUpdate(rowValueMap["UUID"],configID,count)

        return True

    def __updatePieces(self, configID, addCount):

        # 1、是否存在
        isFind = False
        for item in self.piecesContainer.values():
            if item["itemID"] != configID or item["state"] == DBState.Del:
                continue
            isFind = True
            curCount = item["amount"]

            item["amount"] = curCount + addCount

            if item["state"] != DBState.Insert:
                item["state"] = DBState.Update
            self.noticeClientBagUpdate(item["UUID"], configID, curCount + addCount)
            break
        if isFind == True:
            return True
        return self.__insertPieces(configID, addCount)

    # 存储数据库
    def onTimerSyncPieceDB(self):
        delKeys = []
        for item in self.piecesContainer.values():
            state = item["state"]

            # 增加
            if state == DBState.Insert:
                self.insertPieceDB(item)
            # 更新
            elif state == DBState.Update:
                self.updatePieceDB(item)
            # 删除
            elif state == DBState.Del:
                self.delPieceDB(item)
                delKeys.append(item["UUID"])
        for key in delKeys:
            del self.piecesContainer[key]

    def insertPieceDB(self,item):
        # 自己写数据库
        rowValueMap = {}
        rowValueMap["roleID"] = self.databaseID
        rowValueMap["UUID"] = item["UUID"]
        rowValueMap["itemID"] = item["itemID"]
        rowValueMap["amount"] = item["amount"]

        item["state"] = DBState.NoAction

        sql = util.getInsertSql("tbl_ItemPieces", rowValueMap)

        KBEngine.executeRawDatabaseCommand(sql)

        pass
    def updatePieceDB(self,item):
        setMap = {"amount": item["amount"]}
        filterMap = {"roleID": self.databaseID, "UUID": item["UUID"]}
        item["state"] = DBState.NoAction
        sql = util.getUpdateSql("tbl_ItemPieces", setMap, filterMap)

        KBEngine.executeRawDatabaseCommand(sql)

    def delPieceDB(self,item):
        filterMap = {"roleID": self.databaseID, "UUID":  item["UUID"]}
        sql = util.getDelSql("tbl_ItemPieces", filterMap)

        KBEngine.executeRawDatabaseCommand(sql)

class PiecesItemKeys:
    uuid = "UUID"
    itemID = "itemID"
    amount = "amount"
    itemState = "state"

class DBState:

    NoAction = -1
    Insert = 0
    Update = 1
    Del = 2
