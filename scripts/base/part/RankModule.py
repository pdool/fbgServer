# -*- coding: utf-8 -*-
import gameShopConfig
from KBEDebug import *
from ErrorCode import GameShopModuleError

__author__ = 'yanghao'


class RankModule:
    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        # 刷新排行榜自己的数据

        pass
        # --------------------------------------------------------------------------------------------
        #                              客户端调用函数
        # --------------------------------------------------------------------------------------------

    # 请求战斗力排行
    def onClientGetFightValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetFightValueRank", param)

    # 请求等级排行
    def onClientGetLevelValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetLevelValueRank", param)

    # 请求财富排行
    def onClientGetMoneyValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetMoneyValueRank", param)

    # 请求官职排行
    def onClientGetOfficialValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetOfficialValueRank", param)

    # 请求球员排行
    def onClientGetBallerValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetBallerValueRank", param)

    # 请求公会排行
    def onClientGetGuildValueRank(self, page):
        param = {
            "playerMB": self,
            "dbid": self.databaseID,
            "page": page
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetGuildValueRank", param)

    def onClientGetMySelfValueRank(self, dbid,tabName):
        param = {
            "playerMB": self,
            "dbid": dbid,
            "tabName":tabName
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdGetMySelfValueRank", param)
        # --------------------------------------------------------------------------------------------
        #                              工具函数调用函数
        # --------------------------------------------------------------------------------------------

    def updateFightValueRank(self):
        param = {
            "dbid": self.databaseID,
            "name": self.name,
            "camp": self.camp,
            "level": self.level,
            "fightValue": self.fightValue,
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateFightValueRank", param)

    def updateLevelValueRank(self):
        param = {
            "dbid": self.databaseID,
            "name": self.name,
            "camp": self.camp,
            "level": self.level,
            "guildName": self.guildName,
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateLevelValueRank", param)


    def updateMoneyValueRank(self):
        param = {
            "dbid": self.databaseID,
            "name": self.name,
            "camp": self.camp,
            "euro": self.euro,
            "guildName": self.guildName,
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateMoneyValueRank", param)


    def updateOfficalValueRank(self):
        param = {
            "dbid": self.databaseID,
            "name": self.name,
            "camp": self.camp,
            "achievements": self.fame,
            "officalPosition": self.officialPosition,
        }

        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateOfficalValueRank", param)

    def updateBallerValueRank(self,card):
        param = {
            "dbid": card.id,
            "name": self.name,
            "camp": self.camp,
            "level": card.level,
            "cardFightValue":card.fightValue,
            "cardConfigID": card.configID,

        }
        rankMgr = KBEngine.globalData["RankMgr"]

        rankMgr.onCmd("onCmdUpdateBallerValueRank", param)

