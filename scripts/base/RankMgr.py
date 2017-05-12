# -*- coding: utf-8 -*-
import KBEngine
from ErrorCode import CardMgrModuleError
from KBEDebug import ERROR_MSG
from interfaces.BaseModule import BaseModule
__author__ = 'chongxin'


class RankMgr(BaseModule):
    def __init__(self):
        KBEngine.Base.__init__(self)
        KBEngine.globalData["RankMgr"] = self
        ERROR_MSG(" RankMgr ")

    #  刷新战斗力排行
    def onCmdUpdateFightValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["name"] = param["name"]
        playerItem["level"] = param["level"]
        playerItem["camp"] = param["camp"]
        playerItem["fightValue"] = param["fightValue"]
        self.updateValueByType(playerItem, "fightValue", param, self.fightRankList)

    # 刷新等级排行
    def onCmdUpdateLevelValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["name"] = param["name"]
        playerItem["level"] = param["level"]
        playerItem["camp"] = param["camp"]
        playerItem["guildName"] = param["guildName"]
        self.updateValueByType(playerItem, "level", param, self.levelRankList)

    # 刷新财富排行
    def onCmdUpdateMoneyValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["name"] = param["name"]
        playerItem["euro"] = param["euro"]
        playerItem["camp"] = param["camp"]
        playerItem["guildName"] = param["guildName"]
        self.updateValueByType(playerItem, "euro", param, self.moneyRankList)

    # 刷新官职排行
    def onCmdUpdateOfficalValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["name"] = param["name"]
        playerItem["achievements"] = param["achievements"]
        playerItem["officalPosition"] = param["officalPosition"]
        playerItem["camp"] = param["camp"]
        self.updateValueByType(playerItem, "officalPosition", param, self.officalRankList)

    def onCmdUpdateGuildValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["guildName"] = param["guildName"]
        playerItem["camp"] = param["camp"]
        playerItem["level"] = param["level"]
        playerItem["leader"] = param["leader"]
        playerItem["reputation"] = param["reputation"]
        playerItem["guildFunds"] = param["guildFunds"]
        rankList = self.guildRankList
        findItem = None
        for item in rankList:
            if item["dbid"] == playerItem["dbid"]:
                findItem = item
                break
        if findItem is None:
            if len(rankList) <= 0:
                rankList.append(playerItem)
            else:
                isInsert = False
                for i in range(len(rankList)):
                    if playerItem["level"] > rankList[i]["level"]:
                        rankList.insert(i, playerItem)
                        isInsert = True
                        break
                    elif playerItem["level"] == rankList[i]["level"]:
                        if playerItem["reputation"] > rankList[i]["reputation"]:
                            rankList.insert(i, playerItem)
                            isInsert = True
                            break
                if isInsert is False and len(rankList) < 100:
                    rankList.append(playerItem)
        else:
            rankList.remove(findItem)
            if len(rankList) == 0:
                rankList.append(playerItem)
            else:
                for i in range(len(rankList)):
                    if playerItem["level"] > rankList[i]["level"]:
                        rankList.insert(i, playerItem)
                        break
                    elif playerItem["level"] == rankList[i]["level"]:
                        if playerItem["reputation"] > rankList[i]["reputation"]:
                            rankList.insert(i, playerItem)
                            break
                    if i == len(rankList) - 1 and len(rankList) < 100:
                        rankList.append(playerItem)
        if len(rankList) >= 101:
            rankList.pop()

    # 刷新球员排行
    def onCmdUpdateBallerValueRank(self, param):
        # 1、判断是否在榜
        # 2、查找插入的位置
        playerItem = {}
        playerItem["dbid"] = param["dbid"]
        playerItem["name"] = param["name"]
        playerItem["camp"] = param["camp"]
        playerItem["level"] = param["level"]
        playerItem["cardFightValue"] = param["cardFightValue"]
        playerItem["cardConfigID"] = param["cardConfigID"]
        rankList =  self.ballerRankList
        findItem = None
        for item in rankList:
            if item["dbid"] == playerItem["dbid"]:
                findItem = item
                break
        if findItem is None:
            if len(rankList) <= 0:
                rankList.append(playerItem)
            else:
                isInsert = False
                for i in range(len(rankList)):
                    if playerItem["cardFightValue"] > rankList[i]["cardFightValue"]:
                        rankList.insert(i, playerItem)
                        isInsert = True
                        break
                    elif playerItem["cardFightValue"] == rankList[i]["cardFightValue"]:
                        if playerItem["level"] > rankList[i]["level"]:
                            rankList.insert(i, playerItem)
                            isInsert = True
                            break
                if isInsert is False and len(rankList) < 100:
                    rankList.append(playerItem)
        else:
            rankList.remove(findItem)
            if len(rankList) == 0:
                rankList.append(playerItem)
            else:
                for i in range(len(rankList)):
                    if playerItem["cardFightValue"] > rankList[i]["cardFightValue"]:
                        rankList.insert(i, playerItem)
                        break
                    elif playerItem["cardFightValue"] == rankList[i]["cardFightValue"]:
                        if playerItem["level"] > rankList[i]["level"]:
                            rankList.insert(i, playerItem)
                            break
                    if i == len(rankList) - 1 and len(rankList) < 100:
                        rankList.append(playerItem)
        if len(rankList) >= 101:
            rankList.pop()



    def updateValueByType(self, playerItem, listName, param, rankList):
        findItem = None
        for item in rankList:
            if item["dbid"] == playerItem["dbid"]:
                findItem = item
                break
        if findItem is None:
            if len(rankList) <= 0:
                rankList.append(playerItem)
            else:
                isInsert = False
                for i in range(len(rankList)):
                    if playerItem[listName] > rankList[i][listName]:
                        rankList.insert(i, playerItem)
                        isInsert = True
                        break
                if isInsert is False  and len(rankList) < 100:
                    rankList.append(playerItem)
        else:
            rankList.remove(findItem)
            if len(rankList) == 0:
                rankList.append(playerItem)
            else:
                for i in range(len(rankList)):
                    if playerItem[listName] > rankList[i][listName]:
                        rankList.insert(i, playerItem)
                        break
                    if i == len(rankList) - 1 and len(rankList) < 100:
                        rankList.append(playerItem)
        if len(rankList) >= 101:
            rankList.pop()


    # 请求战斗力排行
    def onCmdGetFightValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.fightRankList) > i:
                rankList.append(self.fightRankList[i])
        playerMB.client.onGetFightValue(rankList, len(self.fightRankList))

    # 请求等级排行
    def onCmdGetLevelValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.levelRankList) > i:
                rankList.append(self.levelRankList[i])
        playerMB.client.onGetLevelValue(rankList, len(self.levelRankList))

    # 请求财富排行
    def onCmdGetMoneyValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.moneyRankList) > i:
                rankList.append(self.moneyRankList[i])
        playerMB.client.onGetMoneyValue(rankList, len(self.moneyRankList))

    # 请求官职排行
    def onCmdGetOfficialValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.officalRankList) > i:
                rankList.append(self.officalRankList[i])
        playerMB.client.onGetOfficalValue(rankList, len(self.officalRankList))


    # 请求球员排行
    def onCmdGetBallerValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.ballerRankList) > i:
                rankList.append(self.ballerRankList[i])
        playerMB.client.onGetBallerValue(rankList, len(self.ballerRankList))

    # 请求公会排行
    def onCmdGetGuildValueRank(self, param):
        playerMB = param["playerMB"]
        page = param["page"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize

        rankList = []

        for i in range(start, end):
            if len(self.guildRankList) > i:
                rankList.append(self.guildRankList[i])
        playerMB.client.onGetGuildValue(rankList, len(self.guildRankList))


    # 请求自己当前排名
    def onCmdGetMySelfValueRank(self, param):
        playerMB = param["playerMB"]
        dbid = param["dbid"]
        tabName = param["tabName"]
        if tabName == "fightValue":
            for i in range(len(self.fightRankList)):
                if self.fightRankList[i]["dbid"] == dbid:
                    playerMB.onClientGetFightValueRank(int(i / 7))
                    playerMB.client.onGetMySelfRank(i + 1)
                    return
        elif tabName == "level":
            for i in range(len(self.levelRankList)):
                if self.levelRankList[i]["dbid"] == dbid:
                    playerMB.onClientGetLevelValueRank(int(i / 7))
                    playerMB.client.onGetMySelfRank(i + 1)
                    return
        elif tabName == "euro":
            for i in range(len(self.moneyRankList)):
                if self.moneyRankList[i]["dbid"] == dbid:
                    playerMB.onClientGetMoneyValueRank(int(i / 7))
                    playerMB.client.onGetMySelfRank(i + 1)
                    return
        elif tabName == "officalPosition":
            for i in range(len(self.officalRankList)):
                if self.officalRankList[i]["dbid"] == dbid:
                    playerMB.onClientGetOfficialValueRank(int(i / 7))
                    playerMB.client.onGetMySelfRank(i + 1)
                    return