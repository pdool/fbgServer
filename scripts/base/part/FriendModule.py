# -*- coding: utf-8 -*-

from ErrorCode import FriendError
from KBEDebug import *
import friendConfig

__author__ = 'chongxin'

"""
    对好友列表的一些考虑
    1、好友列表信息定时动态刷新，每次拉取刷新（每次拉取）
"""

class FriendModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):

        self.friendInfoList =[]
        self.applyFriendInfoList = []
        self.blackFriendInfoList = []
        self.recommendInfoList = []
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 获得好友列表
    def onClientGetFriendList(self):
        palyeMgr = KBEngine.globalData["PlayerMgr"]
        self.friendInfoList = []
        self.friendRetFlagSet = set(self.friendDBIDList)

        if len(self.friendDBIDList) == 0:
            friends = {}
            friends["values"] = []
            self.client.onGetFriendInfo(friends)
            return
        ERROR_MSG("     onClientGetFriendList    ")
        for dbid in self.friendDBIDList:
            palyeMgr.queryPlayerInfo(dbid,"onCmdQueryMyInfo",self,"onCmdRetFriendInfo")

    # 获得申请列表
    def onClientGetApplyList(self):
        palyeMgr = KBEngine.globalData["PlayerMgr"]

        if len(self.applyDBIDList) == 0:
            friends = {}
            friends["values"] = []
            self.client.onGetApplyInfo(friends)
            ERROR_MSG("-------------------------  onClientGetApplyList   len is o  -------------------------------")
            return

        self.ApplyRetFlagSet = set(self.applyDBIDList)
        self.applyFriendInfoList = []
        for dbid in self.applyDBIDList:
            palyeMgr.queryPlayerInfo(dbid, "onCmdQueryMyInfo", self, "onCmdRetApplyFriendInfo")

        ERROR_MSG("-------------------------  onClientGetApplyList  -------------------------------")
        pass

    # 获得黑名单列表
    def onClientGetBlackList(self):
        palyeMgr = KBEngine.globalData["PlayerMgr"]

        if len(self.blackDBIDList) == 0:
            friends = {}
            friends["values"] = []
            self.client.onGetBlackInfo(friends)
            return

        self.blackRetFlagSet = set(self.blackDBIDList)
        self.blackFriendInfoList = []
        for dbid in self.blackDBIDList:
            palyeMgr.queryPlayerInfo(dbid, "onCmdQueryMyInfo", self, "onCmdRetBlackFriendInfo")
        pass
    # 获得发现列表
    def onClientRecommendList(self):

        palyeMgr = KBEngine.globalData["PlayerMgr"]
        selfLevel = self.level
        self.recommendInfoList = []
        excludeList = self.friendDBIDList + self.applyDBIDList
        excludeList.append(self.databaseID)
        palyeMgr.getRecommendList(excludeList,selfLevel, self, "onCmdRetRecommendList")
        pass

    # 申请加为好友
    def onClientApplyAddFriend(self,dbid):

        DEBUG_MSG("---------------------onClientApplyAddFriend------------------------------------------------------" + str(dbid))
        if dbid in self.friendDBIDList:
        #     已经是好友了
            self.client.onFriendError(FriendError.Friend_already_is_friend,"")
            return
        if dbid in self.blackDBIDList:
        #     在黑名单
            self.client.onFriendError(FriendError.Friend_he_is_in_black, "")
            return
        # 好友已满
        if len(self.friendDBIDList) >= friendConfig.friendConfig[1]["maxFriendCount"]:
            self.client.onFriendError(FriendError.Friend_list_is_full, "")
            return

        args = {"applyDBID":self.databaseID}
        # KBEngine.globalData["PlayerMgr"].onCmdByDBID(dbid, "onCmdRecvFriendApply", args)
        KBEngine.globalData["PlayerMgr"].onReqAddFriend(dbid, "onCmdRecvFriendApply", self.databaseID)
        pass
    # 同意加好友
    def onClientAgreeAddFriend(self,dbid):

        DEBUG_MSG("-------------onClientAgreeAddFriend---------------------" + str(dbid))
        if dbid in self.friendDBIDList:
        #     已经是好友了
            self.client.onFriendError(FriendError.Friend_already_is_friend, "")
            DEBUG_MSG("---------onClientAgreeAddFriend  is friend----------------------------------------------")
            return
        if dbid in self.blackDBIDList:
        #     在黑名单
            self.client.onFriendError(FriendError.Friend_he_is_in_black, "")
            DEBUG_MSG("---------onClientAgreeAddFriend  is in blacklist----------------------------------------------")
            return
        if dbid  in self.applyDBIDList:
            self.applyDBIDList.remove(dbid)
        else:
            # 不在申请表
            self.client.onFriendError(FriendError.Friend_has_not_apply, "")
            DEBUG_MSG("---------onClientAgreeAddFriend  he is not in applyDBIDList----------------------------------------------")
            return

        if dbid not in self.friendDBIDList:
            self.friendDBIDList.append(dbid)
            self.writeToDB()

        self.onClientGetFriendList()
        palyeMgr = KBEngine.globalData["PlayerMgr"]
        palyeMgr.onAcceptAddFriend(self.databaseID, dbid,"onCmdAcceptAdd")
    # 全部同意
    def onClientAgreeAllAddFriend(self):
        for dbid in self.applyDBIDList:
            self.onClientAgreeAddFriend(dbid)

        self.onClientGetFriendList()
        pass
    # 拒绝加好友
    def onClientRejectAddFriend(self, dbid):

        self.applyDBIDList.remove(dbid)
        # 通知对方，拒绝了你的邀请
        # KBEngine.globalData["PlayerMgr"].onCmdByDBID(dbid, "onCmdRecvFriendApply", {})
        # self.client.onGetFriendInfo()
        pass
    # 全部拒绝加好友
    def onClientRejectAllAddFriend(self):
        for dbid in self.applyDBIDList:
            self.onClientRejectAddFriend(dbid)
        pass

    # 删除好友
    def onClientDelFriend(self,dbid):
        if dbid in self.friendDBIDList:
            self.friendDBIDList.remove(dbid)

            DEBUG_MSG("-------onClientDelFriend----------------------" + str(dbid))


            palyeMgr = KBEngine.globalData["PlayerMgr"]
            palyeMgr.onDelYouFriend(self.databaseID, dbid, "onCmdDelYou")
        else:
        #     不是好友
            return
        pass
    # 加入黑名单
    def onClientAddBlack(self,dbid):
        if dbid not in self.friendDBIDList:
        #     不是好友不能加黑名单
            self.client.onFriendError(FriendError.Friend_is_not_friend, "")
            return
        if dbid in self.blackDBIDList:
        #     已经在黑名单了
            self.client.onFriendError(FriendError.Friend_already_in_black, "")
            return

        if dbid in self.friendDBIDList:
            # self.onClientDelFriend(dbid)
            self.friendDBIDList.remove(dbid)
        if dbid not in self.blackDBIDList:
            self.blackDBIDList.append(dbid)
        if dbid  in self.applyDBIDList:
            self.friendDBIDList.remove(dbid)


    def onClientQueryFriendInfo(self,dbid):
        palyeMgr = KBEngine.globalData["PlayerMgr"]
        palyeMgr.onQueryFriendInfo(dbid, "onCmdQueryMyInfo", self, "onCmdRetQueryFriendInfo")


    def onClientRemoveFromBlack(self,dbid):
        if dbid in self.blackDBIDList:
            self.blackDBIDList.remove(dbid)
            if dbid not in self.friendDBIDList:
                self.friendDBIDList.append(dbid)
        else:
            # 操作错误
            return
    # --------------------------------------------------------------------------------------------
    #                              服务器内部函数调用函数
    # --------------------------------------------------------------------------------------------
    def onCmdRecvFriendApply(self,args):

        applyDBID = args["applyDBID"]

        DEBUG_MSG("-----onCmdRecvFriendApply--------------------"+ str(applyDBID))
        if applyDBID not in self.applyDBIDList:
            self.applyDBIDList.append(applyDBID)
        pass

    def onCmdQueryMyInfo(self,args):
        reqMb = args["reqMB"]
        retMethod = args["retMethod"]

        playerInfo = {}
        playerInfo[FriendInfoKey.DBID] = self.databaseID
        playerInfo[FriendInfoKey.photoIndex] = self.photoIndex
        playerInfo[FriendInfoKey.name] = self.name

        playerInfo[FriendInfoKey.level] = self.level
        playerInfo[FriendInfoKey.clubName] = self.club
        playerInfo[FriendInfoKey.fightValue] = self.fightValue
        playerInfo[FriendInfoKey.vipLevel] = self.vipLevel
        playerInfo[FriendInfoKey.onlineState] = FriendOnlineState.online
        playerInfo[FriendInfoKey.formation] = self.formation
        param = {"playerInfo":playerInfo}
        reqMb.onPlayerMgrCmd(retMethod,param)


    def onCmdRetFriendInfo(self, args):
        playerInfo  = args["playerInfo"]
        dbid = playerInfo[FriendInfoKey.DBID]

        ERROR_MSG("-----onCmdRetFriendInfo-------------get the playerInfo--------------------" + str(playerInfo["name"]) + "-----------" + str(len(self.friendInfoList)))

        if dbid in self.friendRetFlagSet:
            if len(self.friendRetFlagSet) == 1:
                self.friendInfoList.append(playerInfo)
                ERROR_MSG("   -------------friendRetFlagSet---------------      "+ str(playerInfo["name"]))
                friends = {}
                friends["values"] = self.friendInfoList

                self.client.onGetFriendInfo(friends)
                return
            self.friendRetFlagSet.remove(dbid)
            self.friendInfoList.append(playerInfo)
        else:
            return


        pass
    def onCmdRetApplyFriendInfo(self, args):
        DEBUG_MSG("--------onCmdRetApplyFriendInfo----------get the playerInfo--------------------")

        playerInfo  = args["playerInfo"]
        dbid = playerInfo[FriendInfoKey.DBID]
        if dbid in self.ApplyRetFlagSet:
            if len(self.ApplyRetFlagSet) == 1:
                self.applyFriendInfoList.append(playerInfo)
                self.ApplyRetFlagSet.remove(dbid)
                friends = {}
                friends["values"] = self.applyFriendInfoList

                ERROR_MSG("get the playerInf   " + str(len(self.applyFriendInfoList)))
                self.client.onGetApplyInfo(friends)
                return
            self.ApplyRetFlagSet.remove(dbid)
            self.applyFriendInfoList.append(playerInfo)
        else:
            return

    def onCmdRetBlackFriendInfo(self, args):
        DEBUG_MSG("---------onCmdRetBlackFriendInfo---------get the playerInfo--------------------")

        playerInfo = args["playerInfo"]
        dbid = playerInfo[FriendInfoKey.DBID]
        if dbid in self.blackRetFlagSet:
            if len(self.blackRetFlagSet) == 1:
                self.blackFriendInfoList.append(playerInfo)
                friends = {}
                friends["values"] = self.blackFriendInfoList
                self.client.onGetBlackInfo(friends)
                return
            self.blackRetFlagSet.remove(dbid)
            self.blackFriendInfoList.append(playerInfo)
        else:
            return


    def onCmdRetRecommendList(self, args):
        DEBUG_MSG("-----------onCmdRetRecommendList-------get the playerInfo--------------------")
        playerInfoList  = args["recommendList"]

        friends = {}
        friends["values"] = playerInfoList
        self.client.onGetRecommendInfo(friends)

    def onCmdRetQueryFriendInfo(self,args):

        if "playerInfo" in args:

            DEBUG_MSG("-------onCmdRetQueryFriendInfo----------exist-------------------         ")
            playerInfo = args["playerInfo"]

            ERROR_MSG("onCmdRetQueryFriendInfo   name  "+ str(playerInfo["name"]))
            self.client.onGetQueryInfo(playerInfo)
        else:
            DEBUG_MSG("-------onCmdRetQueryFriendInfo-----------not exist------------------         ")
            self.client.onFriendError(FriendError.Player_not_exist,"")

    def onCmdAcceptAdd(self,args):
        acceptorDBID = args["acceptorDBID"]
        if acceptorDBID in self.friendDBIDList:
            #     已经是好友了
            return
        if acceptorDBID in self.blackDBIDList:
            #     在黑名单
            return

        if acceptorDBID not in self.friendDBIDList:
            self.friendDBIDList.append(acceptorDBID)
        if acceptorDBID  in self.applyDBIDList:
            self.applyDBIDList.remove(acceptorDBID)

        self.onClientGetFriendList()

    def onWasActiveFriendInfo(self, argMap):
        playerMB = argMap["playerMB"]
        avatar = argMap["avatar"]
        param = {
            "fightValue": avatar.fightValue,
            "vipLevel": avatar.vipLevel,
            "slogan": avatar.slogan,
            "club": avatar.club,
            "camp": avatar.camp,
            "playerName": avatar.name,
            "dbid": avatar.databaseID,
            "offical": avatar.officalPosition,
            "level": avatar.level,
            "guildName": avatar.guildName,
        }
        playerMB.client.onGetPlayerInfo(param)

    def onCmdDelYou(self,args):
        delDBID = args["delDBID"]

        DEBUG_MSG("---------------onCmdDelYou-------------------------" + str(delDBID))
        if delDBID in self.friendDBIDList:
            self.friendDBIDList.remove(delDBID)
    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------


    def onTimer(self, tid, userArg):


        pass





class FriendInfoKey:
    DBID = "dbid"
    photoIndex= "photoIndex"
    name= "name"
    level = "level"
    vipLevel = "vipLevel"
    fightValue = "fightValue"
    clubName = "clubName"
    onlineState = "onlineState"
    formation = "formation"
class FriendOnlineState:
    online  = -1
























