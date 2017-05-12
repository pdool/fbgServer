# -*- coding: utf-8 -*-
import CommonConfig
import TimerDefine
import util
from ErrorCode import ArenaModuleError, GameShopModuleError
from KBEDebug import *
import ArenaConfig
import ArenaReward

__author__ = 'yangh'
"""
竞技场
"""


class ArenaModule:
    def __init__(self):
        self.isFirstEnter = True
        pass

    def onEntitiesEnabled(self):
        if len(self.arenaInitialList) == 0:
            self.isFirstEnter = True
            return
        self.isFirstEnter = False
        self.client.onGetThreeArenaValue(self.arenaInitialList)
        offset = util.getLeftSecsToNextHMS(0, 0, 0)
        self.addTimer(offset, 24 * 60 * 60, TimerDefine.Timer_arena_reward)
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def onTimer(self, id, userArg):
        if userArg != TimerDefine.Timer_arena_reward:
            return
        if self.myRank > 5000:
            return
        rewardId = 0
        for item in ArenaReward.ArenaReward.values():
            if item["id"] == self.myRank:
                rewardId = item["id"]
                break
            if item["id"] < self.myRank and item["id"] > rewardId:
                rewardId = item["id"]

        config = ArenaReward.ArenaReward[rewardId]
        diamond = config["reward"].split(";")[0]
        self.diamond = self.diamond + int(diamond)
        blackMoney = config["reward"].split(";")[1]
        self.blackMoney = self.blackMoney + int(blackMoney)



    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def onArenaMgrQueryResult(self, itemList):
        clientResult = []
        self.chanllengeMap = {}
        self.arenaInitialList = []
        inStr = ""
        for i in range(len(itemList)):
            dbid = itemList[i]["dbid"]
            rank = itemList[i]["rank"]
            isRobot = itemList[i]["isRobot"]

            self.chanllengeMap[dbid] = {"rank":rank,"isRobot": isRobot,"inTeamCardIDDict":{}}
            if isRobot == 1:
                # 填充配置文件
                clientResultItem  = {}
                config = ArenaConfig.ArenaConfig[dbid]
                clientResultItem["dbid"] = dbid
                clientResultItem["rank"] = rank
                clientResultItem["name"] = config["playerName"]
                clientResultItem["club"] = config["clubName"]
                clientResultItem["formation"] = config["campId"]
                clientResultItem["camp"] = config["camp"]
                clientResultItem["fightValue"] = config["fightValue"]
                clientResult.append(clientResultItem)
                self.arenaInitialList.append(clientResultItem)
                continue
            clientResultItem = {}
            clientResultItem["dbid"] = dbid
            clientResultItem["rank"] = rank
            clientResultItem["name"] = ""
            clientResultItem["club"] = ""
            clientResultItem["formation"] = 1
            clientResultItem["camp"] = 1
            clientResultItem["fightValue"] = 1
            clientResult.append(clientResultItem)
            self.arenaInitialList.append(clientResultItem)
            inStr = inStr + str(dbid)  + ","

        if inStr != "":
            inStr = inStr[:-1]

            @util.dbDeco
            def cb(result, rownum, error):
                if result is not  None:
                    for i in range(len(result)):
                        dbid = int(result[i][0])
                        name = result[i][1].decode('utf-8')
                        club = result[i][2].decode('utf-8')
                        formation = int(result[i][3])
                        fightValue = int(result[i][4])
                        cardConfigID = int(result[i][5])
                        skill1 = int(result[i][6])
                        skill2 = int(result[i][7])
                        camp = int(result[i][8])
                        item = self.chanllengeMap[dbid]
                        inTeamCardIDDict = item["inTeamCardIDDict"]
                        inTeamCardIDDict[cardConfigID] = {"skill1":skill1,"skill2":skill2}
                        for resultItem in clientResult:
                            if resultItem["dbid"] == dbid:
                                resultItem["name"] = name
                                resultItem["club"] = club
                                resultItem["fightValue"] = fightValue
                                resultItem["formation"] = formation
                                resultItem["camp"] = camp
                        for Item in self.arenaInitialList:
                            if Item["dbid"] == dbid:
                                Item["name"] = name
                                Item["club"] = club
                                Item["fightValue"] = fightValue
                                Item["formation"] = formation
                                Item["camp"] = camp

                self.client.onGetThreeArenaValue(clientResult)

            sql = "SELECT a.id, a.sm_name, a.sm_club, a.sm_formation, a.sm_fightValue,c.sm_configID, c.sm_skill1, c.sm_skill2,a.sm_camp FROM tbl_Avatar AS a, tbl_Card AS c WHERE a.id in("+inStr+") AND c.sm_inTeam = 1"

            KBEngine.executeRawDatabaseCommand(sql,cb)
        else:
            self.client.onGetThreeArenaValue(clientResult)

        self.updateAreanCd = 0
        if self.isFirstEnter == True:
            self.isFirstEnter = False
            return
        self.currentArenaTimes = util.getCurrentTime()
        self.client.onGetUpdateCD(self.updateAreanCd)


    def onArenaMgrValueRankResult(self,itemList):
        clientResult = []
        inStr = ""
        for i in range(len(itemList)):
            dbid = itemList[i]["dbid"]
            rank = itemList[i]["rank"]
            isRobot = itemList[i]["isRobot"]
            count  = itemList[i]["count"]
            if isRobot == 1:
                clientResultItem = {}
                config = ArenaConfig.ArenaConfig[dbid]
                clientResultItem["dbid"] = dbid
                clientResultItem["rank"] = rank
                clientResultItem["name"] = config["playerName"]
                clientResultItem["club"] = config["clubName"]
                clientResultItem["formation"] = config["campId"]
                clientResultItem["camp"] = config["camp"]
                clientResultItem["fightValue"] = config["fightValue"]
                clientResult.append(clientResultItem)
                continue
            clientResultItem = {}
            clientResultItem["dbid"] = dbid
            clientResultItem["rank"] = rank
            clientResultItem["name"] = ""
            clientResultItem["club"] = ""
            clientResultItem["formation"] = 1
            clientResultItem["fightValue"] = 1
            clientResultItem["camp"] = 1
            clientResult.append(clientResultItem)
            inStr = inStr + str(dbid) + ","
        if inStr == "":
            self.client.onGetArenaRankValue(clientResult,count)
            return
        inStr = inStr[:-1]

        @util.dbDeco
        def cb(result, rownum, error):
            if result is not None:
                for i in range(len(result)):
                    dbid = int(result[i][0])
                    name = result[i][1].decode('utf-8')
                    club = result[i][2].decode('utf-8')
                    formation = int(result[i][3])
                    fightValue = int(result[i][4])
                    camp = int(result[i][5])
                    for resultItem in clientResult:
                        if resultItem["dbid"] == dbid:
                            resultItem["name"] = name
                            resultItem["club"] = club
                            resultItem["formation"] = formation
                            resultItem["fightValue"] = fightValue
                            resultItem["camp"] = camp
                self.client.onGetArenaRankValue(clientResult,count)
            pass
        sql = "SELECT a.id, a.sm_name, a.sm_club, a.sm_formation, a.sm_fightValue,a.sm_camp FROM tbl_Avatar AS a, tbl_Card AS c WHERE a.id in(" + inStr + ") AND c.sm_inTeam = 1"
        KBEngine.executeRawDatabaseCommand(sql, cb)

    # 请求玩家信息
    def onClientGetArenaPlayerInfo(self,rank):
        param = {
            "playerMB": self,
            "rank": rank,
        }

        arenaMgr = KBEngine.globalData["ArenaMgr"]
        arenaMgr.onCmd("onCmdGetArenaPlayerInfo", param)

    def onGetArenaPlayerInfo(self,param):
        for i in range(len(param)):
            dbid = param[i]["dbid"]
            isRobot = param[i]["isRobot"]

            if  isRobot == 0 :
                self.onClientGetPlayerInfo(dbid)
            else:
                config = ArenaConfig.ArenaConfig[dbid]
                param = {
                    "fightValue": config["fightValue"],
                    "vipLevel": config["vip"],
                    "slogan": config["slogan"],
                    "club": config["clubName"],
                    "camp": config["camp"],
                    "playerName": config["playerName"],
                    "dbid": dbid,
                    "offical": config["offical"],
                    "level": config["level"],
                    "guildName": config["guild"],
                }
                self.client.onGetPlayerInfo(param)





    # 初始化自己的排行
    def defaultMyRank(self,param):
        rank = param["rank"]
        self.myRank = rank
        self.onClientUpdateArenaRank()

    # 刷新自己的排行榜
    def onUpdateRank(self,enemyDBID,enemyRank):
        param = {
            "selfRank": self.myRank,
            "selfDBID": self.databaseID,
            "enemyDBID": enemyDBID,
            "enemyRank": enemyRank,
        }
        arenaMgr = KBEngine.globalData["ArenaMgr"]
        arenaMgr.onCmd("onCmdUpdateArenaRank",param)

    def onClientStartArenaPVP(self):
        if self.arenaTimes == 0:
            return
        self.arenaTimes = self.arenaTimes - 1

    # 请求倒计时
    def onClientGetUpdateCD(self):
        self.updateAreanCd = util.getCurrentTime() - self.currentArenaTimes
        if self.updateAreanCd >= 10:
            return
        self.client.onGetUpdateCD(self.updateAreanCd)

    # 请求竞技场排行榜
    def onClientGetArenaRank(self,page):
        param = {
            "playerMB": self,
            "page": page,
        }
        arenaMgr = KBEngine.globalData["ArenaMgr"]
        arenaMgr.onCmd("onCmdGetArenaRankValue", param)


    # 刷新竞技对手排行榜
    def onClientUpdateArenaRank(self):
        param = {
            "selfRank": self.myRank,
            "playerMB": self,
        }
        arenaMgr = KBEngine.globalData["ArenaMgr"]
        arenaMgr.onCmd("onCmdGetChanllengeMember", param)

    # 购买挑战次数
    def onClientBuyArenaTimes(self):
        if self.buyArenaTimes == 0:
            self.client.onArenaCallBack(ArenaModuleError.Buy_times_is_not_enough)
            return
        money = CommonConfig.CommonConfig[7]["value"]
        if self.diamond < money:
            self.client.onShopInfoCallBack(GameShopModuleError.Diamod_not_enough)
            return
        self.diamond = self.diamond - money
        self.buyArenaTimes = self.buyArenaTimes - 1
        self.arenaTimes = CommonConfig.CommonConfig[6]["value"]
        self.client.onArenaCallBack(ArenaModuleError.Buy_times_is_Sucess)

    # 请求战绩数据
    def onClientGetRecord(self):
        self.client.onGetRecord(self.recordList)

    # 加入竞技场排行
    def onAddArenaRank(self):
        param = {
            "selfDBID": self.databaseID,
            "isRobot": 0,
            "playerMB": self,
        }
        arenaMgr = KBEngine.globalData["ArenaMgr"]
        arenaMgr.onCmd("onCmdInsertArenaRank", param)