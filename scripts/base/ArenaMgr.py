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

    def onCmdGetArenaRankValue(self, param):
        page = param["page"]
        playerMB = param["playerMB"]

        pageSize = 7

        start = pageSize * page
        end = start + pageSize
        sql = "select sm_dbid,sm_rank,sm_isRobot from tbl_ArenaRow where sm_rank  between " + str(start) + " and " + str(end)



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
                    "isRobot": isRobot
                }
                param.append(item)
            playerMB.onPlayerMgrCmd("onArenaMgrValueRankResult", param)
        KBEngine.executeRawDatabaseCommand(sql, rankResult)



    def onCmdGetChanllengeMember(self,param):
        selfRank = param["selfRank"]
        playerMB = param["playerMB"]
        rankNum = 3
        down = selfRank - 100
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
        selfDBID = param["selfDBID"]
        enemyDBID = param["enemyDBID"]
        enemyRank = param["enemyRank"]

        setMap= {"rank":selfRank}
        filterMap = {"dbid":selfDBID}
        sql1 = util.getUpdateSql("tbl_ArenaRow",setMap,filterMap)
        KBEngine.executeRawDatabaseCommand(sql1)

        setMap2 = {"rank": enemyRank}
        filterMap2 = {"dbid": enemyDBID}
        sql2 = util.getUpdateSql("tbl_ArenaRow", setMap2, filterMap2)
        KBEngine.executeRawDatabaseCommand(sql2)

    def onCmdInsertArenaRank(self,param):
        selfDBID = param["selfDBID"]
        isRobot = param["isRobot"]
        sql = "INSERT INTO tbl_ArenaRow (sm_dbid, sm_rank,sm_isRobot)VALUES("+str(selfDBID)+","+"(	SELECT IFNULL(max(t.sm_rank) + 1,1) FROM tbl_ArenaRow t),"+str(isRobot)+")"

        def cb(result, rownum, error):
            if isRobot == 0:
                sql1 = "SELECT sm_rank FROM tbl_ArenaRow AS a WHERE a.sm_dbid = " + str(
                    selfDBID) + "  AND a.sm_isRobot = 0"
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

        KBEngine.executeRawDatabaseCommand(sql,cb)




# if __name__=="__main__":
#     param = {"selfDBID":111}
#
#     onCmdInsertArenaRank(None,param)

