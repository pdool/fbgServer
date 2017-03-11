# -*- coding: utf-8 -*-
from ErrorCode import ChatError
from part.FriendModule import FriendInfoKey, FriendOnlineState

__author__ = 'chongxin'


import KBEngine
import util
from KBEDebug import *
import friendConfig
import random

class PlayerMgr(KBEngine.Base):


    def __init__(self):
        KBEngine.Base.__init__(self)
        KBEngine.globalData["PlayerMgr"] = self
        # 在线列表
        self.dbidToMailBox ={}
        # 离线玩家列表信息
        self.dbidToOfflinePlayerInfo = {}
        # 所有玩家信息
        self.allPlayerInfo = []
        # 初始化离线数据
        self.initOfflineData()
        pass

    @staticmethod
    def getPlayerMgr():
        mgr = KBEngine.globalData["PlayerMgr"]
        if mgr is None:
            ERROR_MSG("PlayerMgr is None")
        return mgr


    # 上线玩家注册
    def playerLogin(self,playerMB,dbID,playerInfo):

        self.dbidToMailBox[dbID] = playerMB

        # 更新玩家信息
        if playerInfo not in self.allPlayerInfo:
            for item in self.allPlayerInfo:
                if item[FriendInfoKey.DBID] == playerInfo[FriendInfoKey.DBID]:
                    self.allPlayerInfo.remove(item)
                    break
            self.allPlayerInfo.append(playerInfo)
            self.allPlayerInfo.sort(key=lambda x: (x[FriendInfoKey.onlineState],x[FriendInfoKey.level]))



        if dbID in self.dbidToOfflinePlayerInfo:
            del self.dbidToOfflinePlayerInfo[dbID]

    def playerOffline(self,dbID,playerInfo):
        if dbID in self.dbidToMailBox:
            del self.dbidToMailBox[dbID]
        self.dbidToOfflinePlayerInfo[dbID] = playerInfo
        if playerInfo not in self.allPlayerInfo:
            for item in self.allPlayerInfo:
                if item[FriendInfoKey.DBID] == playerInfo[FriendInfoKey.DBID]:
                    self.allPlayerInfo.remove(item)
                    break
            self.allPlayerInfo.append(playerInfo)
            self.allPlayerInfo.sort(key=lambda x: (x[FriendInfoKey.onlineState], x[FriendInfoKey.level]))

    def onCmdByDBID(self,otherDBId,funcName,argDict):
        # 如果在线
        DEBUG_MSG("----------onCmdByDBID---------------- " + funcName)
        if otherDBId in self.dbidToMailBox and self.dbidToMailBox[otherDBId] is not None:

            mb = self.dbidToMailBox[otherDBId]
            mb.onPlayerMgrCmd(funcName,argDict)
        else:
            DEBUG_MSG("-------------------------- self.dbidToMailBox[otherDBId] is not None" )


    # 初始化离线数据
    def initOfflineData(self):
        colTuple = ("id", "sm_name", "sm_photoIndex", "sm_level", "sm_club", "sm_fightValue", "sm_vipLevel","sm_logoutTime")
        sql = util.getSelectSql("tbl_Avatar", colTuple)

        def queryResult(result, rownum, error):
            for item in result:
                playerInfo = {}
                playerInfo[FriendInfoKey.DBID] = int(item[0])
                playerInfo[FriendInfoKey.name] = item[1].decode('utf-8')
                playerInfo[FriendInfoKey.photoIndex] = str(item[2])
                playerInfo[FriendInfoKey.level] = int(item[3])
                playerInfo[FriendInfoKey.clubName] = item[4].decode('utf-8')
                playerInfo[FriendInfoKey.fightValue] = int(item[5])
                playerInfo[FriendInfoKey.vipLevel] = int(item[6])
                playerInfo[FriendInfoKey.onlineState] = int(item[7])

                self.dbidToOfflinePlayerInfo[playerInfo[FriendInfoKey.DBID]] = playerInfo

                self.allPlayerInfo.append(playerInfo)
            self.allPlayerInfo.sort(key =lambda x:(x[FriendInfoKey.onlineState],x[FriendInfoKey.level]))

        KBEngine.executeRawDatabaseCommand(sql, queryResult)
    # 查询玩家信息
    """
    toDBID 被查询者的DBID
    toMethod 被查询者调用的方法
    retMb 查询人的MB
    retMethod 查询人接收的方法
    """
    def queryPlayerInfo(self,toDBID,toMethod,retMb,retMethod):
        # 在线
        if toDBID in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDBID]
            args = {"reqMB":retMb,"retMethod":retMethod}
            mb.onPlayerMgrCmd(toMethod, args)

        # 离线
        else:
            if toDBID in self.dbidToOfflinePlayerInfo:
                playerInfo = self.dbidToOfflinePlayerInfo[toDBID]
                args={"playerInfo":playerInfo}

                retMb.onPlayerMgrCmd(retMethod,args)
            pass

    # --------------------------------------------------------------------------------------------
    #                              好友模块
    # --------------------------------------------------------------------------------------------

    def getRecommendList(self,excludeList,level,retMb,retMethod):
        # 推荐数量
        recommendCount =friendConfig.friendConfig[1]["recommendCount"]
        recommendList = []
        minLevel = int(level / 10) * 10 + 1
        maxLevel = int(level / 10 + 1) * 10
        # 总共玩家数量
        playerCount = len(self.allPlayerInfo)

        maxIndex = 0
        minIndex = playerCount -1
        ERROR_MSG("playerCount   " + str(playerCount) +"  maxLevel  "+ str(maxLevel) +"  minLevel "+ str(minLevel) )
        # 1、先找到区间

        for i in range(playerCount):
            ERROR_MSG("  i level " + str(self.allPlayerInfo[i][FriendInfoKey.level]) +" dbid  "+ str(self.allPlayerInfo[i][FriendInfoKey.DBID]) )


        for i in range(playerCount):
            ERROR_MSG("  i level   " + str(self.allPlayerInfo[i][FriendInfoKey.level]))
            if self.allPlayerInfo[i][FriendInfoKey.level] <= maxLevel:
                maxIndex = i
                break

        for i in reversed(range(playerCount)):
            if self.allPlayerInfo[i][FriendInfoKey.level] >= minLevel:
                minIndex = i
                break

        excludeSet = set(excludeList)
        canSelectList = list(range(maxIndex,minIndex+1))

        ERROR_MSG("max  " + str(maxIndex) +"  min "+ str(minIndex))

        #2、去除在好友列表和申请列表的以及自己
        for index in canSelectList:
            if self.allPlayerInfo[index][FriendInfoKey.DBID] in excludeSet:
                canSelectList.remove(index)

        canSelectCount = len(canSelectList)
        # 3.1、如果够随机出来
        if canSelectCount >= recommendCount:
            resultIndexList = random.sample(range(0, canSelectCount), recommendCount)
        else:
        #3.2、如果不够，先把区间内的全加进来，然后往两边取
            resultIndexList = canSelectList

            needCount = recommendCount - len(resultIndexList)

            while(needCount >=0 ):
                # 加上部分的
                if maxIndex -1 >= 0:
                    maxIndex = maxIndex -1
                    if self.allPlayerInfo[maxIndex][FriendInfoKey.DBID] not in excludeSet:
                        resultIndexList.append(maxIndex)
                        needCount = needCount -1
                # 加下部分的
                if minIndex + 1 <= playerCount -1:
                    minIndex = minIndex + 1
                    if self.allPlayerInfo[minIndex][FriendInfoKey.DBID] not in excludeSet:
                        resultIndexList.append(minIndex)
                        needCount = needCount -1
                # 两头都到了，退出来

                if maxIndex <= 0 and minIndex >= playerCount-1:
                    break


        for index in set(resultIndexList):
            if self.allPlayerInfo[index][FriendInfoKey.DBID] not in excludeSet:
                recommendList.append(self.allPlayerInfo[index])

        args = {"recommendList": recommendList}

        # return args
        retMb.onPlayerMgrCmd(retMethod, args)
    # 查询玩家信息
    def onQueryFriendInfo(self,toDBID,toMethod,retMb,retMethod):
        # 在线
        if toDBID in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDBID]
            args = {"reqMB": retMb, "retMethod": retMethod}
            mb.onPlayerMgrCmd(toMethod, args)

        # 离线
        elif toDBID in self.dbidToOfflinePlayerInfo:
            playerInfo = self.dbidToOfflinePlayerInfo[toDBID]
            args = {"playerInfo": playerInfo}

            retMb.onPlayerMgrCmd(retMethod, args)
        else:

            retMb.onPlayerMgrCmd(retMethod, {})

    # 申请加为好友
    def onReqAddFriend(self,toDBID,toMethod,applyDBID):
        # 在线
        if toDBID in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDBID]
            args = {"applyDBID": self.databaseID}
            mb.onPlayerMgrCmd(toMethod, args)

        # 离线
        elif toDBID in self.dbidToOfflinePlayerInfo:
            # 直接插入数据库
            rowValueMap = {}
            rowValueMap["parentID"] = toDBID
            rowValueMap["sm_value"] = applyDBID
            sql = util.getInsertSql("tbl_Avatar_applyDBIDList", rowValueMap,False)

            KBEngine.executeRawDatabaseCommand(sql)


    def onAcceptAddFriend(self,selfDBID,toDBID,toMethod):
        # 在线
        if toDBID in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDBID]
            args = {"acceptorDBID": selfDBID}
            mb.onPlayerMgrCmd(toMethod, args)
            DEBUG_MSG("----------onAcceptAddFriend---------online----")
        # 离线
        elif toDBID in self.dbidToOfflinePlayerInfo:
            DEBUG_MSG("----------onAcceptAddFriend---------offline----")
            rowValueMap = {"parentID": toDBID,"sm_value":selfDBID}
            sql = util.getInsertSql("tbl_Avatar_friendDBIDList",rowValueMap,False)

            KBEngine.executeRawDatabaseCommand(sql,None )


    def onDelYouFriend(self,selfDBID,toDBID,toMethod):
        # 在线
        if toDBID in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDBID]
            args = {"delDBID": selfDBID}
            mb.onPlayerMgrCmd(toMethod, args)

        # 离线
        elif toDBID in self.dbidToOfflinePlayerInfo:
            rowValueMap = {"parentID": toDBID,"sm_value":selfDBID}
            sql = util.getDelSql("tbl_Avatar_friendDBIDList",rowValueMap,False)

            KBEngine.executeRawDatabaseCommand(sql,None )
    # --------------------------------------------------------------------------------------------
    #                              聊天模块
    # --------------------------------------------------------------------------------------------
    def sendWorldChat(self,senderDbid,messageInfo):
        for mb in self.dbidToMailBox.values():
            mb.onCmdWorldChat(senderDbid,messageInfo)

    def sendAdChat(self,messageInfo):
        for mb in self.dbidToMailBox.values():
            mb.client.onAdChat(messageInfo)

    def sendPrivateChat(self,toDbid,senderDbid,messageInfo):
        if toDbid in self.dbidToMailBox:
            mb = self.dbidToMailBox[toDbid]
            mb.onCmdPrivateChat(senderDbid,messageInfo)
        else:
            # 玩家下线了
            if senderDbid in self.dbidToMailBox:
                mb = self.dbidToMailBox[senderDbid]
                mb.client.onChatError(ChatError.Chat_player_offline)

if __name__ == "__main__":
    canSelectList = list(range(0, 2))
    for i in canSelectList:
        print(i)


    p = PlayerMgr()

    p.allPlayerInfo =[]

    p.allPlayerInfo.append({"level": 1, "dbid": 1})
    p.allPlayerInfo.append({"level" : 1,"dbid" : 2})

    excludeList = [12]


    l = p.getRecommendList(excludeList,1,None,None)

    for x in l:
        print(x)