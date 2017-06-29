# -*- coding: utf-8 -*-
import KBEngine
import util
import ArenaConfig
from KBEDebug import ERROR_MSG
from interfaces.BaseModule import BaseModule

__author__ = 'yanghao'


"""
竞技场管理器
"""
class ArenaMgr(BaseModule):

    def __init__(self):
        BaseModule.__init__(self)
        KBEngine.globalData["ArenaMgr"] = self
        ERROR_MSG("ArenaMgr   init       ")


    def loadFakeData(self):
        config = ArenaConfig.ArenaConfig
        length = len(config) + 1
        for i in range(1, length):
            param = {
                "selfDBID": i,
                "isRobot" : 1,
            }
            self.onCmdInsertArenaRank(param)


    def onCmdGetArenaPlayerInfo(self,param):
        rank = param["rank"]
        playerMB = param["playerMB"]


        @util.dbDeco
        def getPlayerInfo(result, rownum, error):
            if result is None:
                return
            param = []
            for i in range(len(result)):
                dbid = int(result[i][0])
                isRobot = int(result[i][1])

                item = {
                    "dbid": dbid,
                    "isRobot": isRobot
                }
                param.append(item)
            playerMB.onPlayerMgrCmd("onGetArenaPlayerInfo", param)
        sql = "select sm_dbid,sm_isRobot from tbl_ArenaRow where sm_rank  = " + str(
            rank)

        KBEngine.executeRawDatabaseCommand(sql, getPlayerInfo)

    def onCmdGetArenaAllRankValue(self, argMap):

        @util.dbDeco
        def getRankCount(result, rownum, error):
            count = int(result[0][0])
            sql = "select sm_dbid,sm_rank,sm_isRobot from tbl_ArenaRow"

            ERROR_MSG("--onCmdGetArenaAllRankValue--count"+str(count))

            @util.dbDeco
            def rankResult(result, rownum, error):
                if result is None:
                    return
                param = []
                for i in range(len(result)):
                    dbid = int(result[i][0])
                    rank = int(result[i][1])
                    isRobot = int(result[i][2])

                    item = {
                        "dbid": dbid,
                        "rank": rank,
                        "isRobot": isRobot,
                        "count": count
                    }
                    param.append(item)

                    argMap["areanList"] = param


                leagueMgr = KBEngine.globalData["LeagueMgr"]
                leagueMgr.onCmd("onCmdAreanRankData", argMap)

            KBEngine.executeRawDatabaseCommand(sql, rankResult)

        sql1 = "select count(*) from tbl_ArenaRow "
        KBEngine.executeRawDatabaseCommand(sql1, getRankCount)

    def onCmdGetArenaRankValue(self, param):
        page = param["page"]
        playerMB = param["playerMB"]

        pageSize = 6

        start = pageSize * page + 1
        end = start + pageSize - 1

        @util.dbDeco
        def getRankCount(result, rownum, error):
            count = int(result[0][0])
            sql = "select sm_dbid,sm_rank,sm_isRobot from tbl_ArenaRow where sm_rank  between " + str(
                start) + " and " + str(end)
            @util.dbDeco
            def rankResult(result, rownum, error):
                if result is None:
                    return
                param = []
                for i in range(len(result)):
                    dbid = int(result[i][0])
                    rank = int(result[i][1])
                    isRobot = int(result[i][2])

                    item = {
                        "dbid": dbid,
                        "rank": rank,
                        "isRobot": isRobot,
                        "count": count
                    }
                    param.append(item)
                playerMB.onPlayerMgrCmd("onArenaMgrValueRankResult", param)

            KBEngine.executeRawDatabaseCommand(sql, rankResult)
        sql1 = "select count(*) from tbl_ArenaRow "
        KBEngine.executeRawDatabaseCommand(sql1, getRankCount)




    def onCmdGetChanllengeMember(self,param):
        selfRank = param["selfRank"]
        playerMB = param["playerMB"]
        rankNum = 3
        down = 1000
        if selfRank > 1000:
            down = selfRank - 100
        elif selfRank > 500 and selfRank <= 1000:
            down = selfRank - 20
        elif selfRank > 200 and selfRank <= 500:
            down = selfRank - 15
        elif selfRank > 50 and selfRank <= 200:
            down = selfRank - 10
        elif selfRank > 10 and selfRank <= 50:
            down = selfRank - 8
        elif selfRank > 1 and selfRank <= 10:
            down = selfRank - 5
        # 注意判断下限
        top = selfRank - 1
        sql = "select sm_dbid,sm_rank,sm_isRobot from tbl_ArenaRow where sm_rank  between "+ str(down)+" and " + str(top) +"  ORDER BY rand() LIMIT " + str(rankNum)

        ERROR_MSG("=========slq== " +sql)
        @util.dbDeco
        def queryResult(result, rownum, error):
            if result is None:
                return
            param = []
            for i in range(len(result)):
                dbid = int(result[i][0])
                rank = int(result[i][1])
                isRobot =  int(result[i][2])

                item = {
                    "dbid": dbid,
                    "rank": rank,
                    "isRobot": isRobot
                }
                param.append(item)

            playerMB.onPlayerMgrCmd("onArenaMgrQueryResult",param)
        KBEngine.executeRawDatabaseCommand(sql,queryResult)


    def onCmdUpdateArenaRank(self,param):
        selfRank = param["selfRank"]
        enemyRank = param["enemyRank"]
        ERROR_MSG("--onCmdUpdateArenaRank--selfRank--"+str(selfRank)+"-enemyRank--"+str(enemyRank))

        sql = "update tbl_ArenaRow selfT, tbl_ArenaRow enemy set selfT.sm_dbid = enemy.sm_dbid,enemy.sm_dbid = selfT.sm_dbid ,selfT.sm_isRobot = enemy.sm_isRobot,enemy.sm_isRobot = selfT.sm_isRobot where selfT.sm_rank = " + str(
            selfRank) + " and enemy.sm_rank =" + str(
            enemyRank)

        ERROR_MSG("onCmdUpdateArenaRank  change the rank sql : " + sql)

        KBEngine.executeRawDatabaseCommand(sql)

    def onCmdInsertArenaRank(self,param):
        selfDBID = param["selfDBID"]
        isRobot = param["isRobot"]
        sql = "INSERT INTO tbl_ArenaRow (sm_dbid, sm_rank,sm_isRobot)VALUES("+str(selfDBID)+","+"(	SELECT IFNULL(max(t.sm_rank) + 1,1) FROM tbl_ArenaRow t),"+str(isRobot)+")"

        @util.dbDeco
        def cb(result, rownum, error):
            if isRobot == 0:
                sql1 = "SELECT sm_rank FROM tbl_ArenaRow AS a WHERE a.sm_dbid = " + str(
                    selfDBID) + "  AND a.sm_isRobot = 0"

                @util.dbDeco
                def findMyRank(result, rownum, error):
                    if result is None:
                        return
                    rank = int(result[0][0])
                    playerMB = param["playerMB"]
                    item = {
                        "rank": rank,
                    }
                    playerMB.onPlayerMgrCmd("defaultMyRank", item)

                KBEngine.executeRawDatabaseCommand(sql1, findMyRank)

        KBEngine.executeRawDatabaseCommand(sql,cb,self.id)




# if __name__=="__main__":
#     param = {"selfDBID":111}
#
#     onCmdInsertArenaRank(None,param)

