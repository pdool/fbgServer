# -*- coding: utf-8 -*-
import util
from KBEDebug import *
from ErrorCode import ChatError
import chatConfig
from badWords import badWords

__author__ = 'chongxin'

"""
    聊天
"""

class ChatModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        self.playerMgr = KBEngine.globalData["PlayerMgr"]

        self.worldChanelSendTime = 0
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 世界聊天
    def onClientWorldChat(self,message):
        # 1、消息超过规定长度
        if self.checkMessageLen(message) is False:
            return

        # 2、等级不足
        level = self.level
        levelLimit = chatConfig.ChatConfig[1]["worldChannelLevelLimit"]
        if level < levelLimit:
            self.client.onChatError(ChatError.Chat_world_level_not_enough)
            return

        # 3、世界频道在CD
        curTime = util.getCurrentTime()
        cd = chatConfig.ChatConfig[1]["worldChannelCD"]
        if curTime - self.worldChanelSendTime < cd:
            self.client.onChatError(ChatError.Chat_world_cd)
            return
        # 4、有脏话
        message = self.replaceBadWords(message)

        
        messageInfo = self.makeMessageInfo(message)
        KBEngine.globalData["PlayerMgr"].sendWorldChat( self.databaseID,messageInfo)

    # 公会聊天
    def onClientClubChat(self,message):
        if self.checkMessageLen(message) is False:
            # 消息超过规定长度
            return
        message = self.replaceBadWords(message)
        messageInfo = self.makeMessageInfo(message)
        messageInfo[MessageInfoEnum.clubPosition] = "manager"

        # self.playerMgr.sendClubChat(messageInfo)
       # TODO: 没有工会。暂时不做
    # 广告
    def onClientAdChat(self,message):
        if self.checkMessageLen(message) is False:
            # 消息超过规定长度
            return
        message = self.replaceBadWords(message)
        # 检查道具
        # 检查钻石
        adCost = chatConfig.ChatConfig[1]["adCostDiamond"]
        if self.diamond < adCost:
            self.client.onChatError(ChatError.has_not_enough_diamond)
            return

        self.diamond = self.diamond - adCost

        messageInfo = self.makeMessageInfo(message)

        KBEngine.globalData["PlayerMgr"].sendAdChat(self.databaseID,messageInfo)

    # 私聊
    def onClientPrivate(self,dbid,message):
        if self.checkMessageLen(message) is False:
            # 消息超过规定长度
            return
        message = self.replaceBadWords(message)

        messageInfo = self.makeMessageInfo(message)

        KBEngine.globalData["PlayerMgr"].sendPrivateChat(dbid,self.databaseID,messageInfo)

    # --------------------------------------------------------------------------------------------
    #                              服务器内部函数调用函数
    # --------------------------------------------------------------------------------------------
    def onCmdWorldChat(self,senderDBID,messageInfo):

        ERROR_MSG("----------ad  ------")

        if self.checkInBlack(senderDBID) is True:
            return

        # if messageInfo[MessageInfoEnum.name] == self.name:
        #     return


        self.client.onWorldChat(senderDBID,messageInfo)

    def onCmdPrivateChat(self,senderDBID,messageInfo):
        if self.checkInBlack(senderDBID) is True:
            return
        self.client.onPrivateChat(senderDBID,messageInfo)
    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------
    # 是否在黑名单
    def checkInBlack(self,senderDBID):
        if senderDBID in self.blackDBIDList:
            return True
        return False
    # 包装信息
    def makeMessageInfo(self,message):
        messageInfo = {}
        messageInfo[MessageInfoEnum.message] = message
        messageInfo[MessageInfoEnum.photoIndex] = self.photoIndex
        messageInfo[MessageInfoEnum.name] = self.name
        messageInfo[MessageInfoEnum.level] = self.level
        messageInfo[MessageInfoEnum.vipLevel] = self.vipLevel
        messageInfo[MessageInfoEnum.sendTime] = util.getCurrentTime()
        return  messageInfo
    # 检查消息长度
    def checkMessageLen(self,message):
        if len(message) > chatConfig.ChatConfig[1]["maxMessageLen"]:
            # 消息超过规定长度
            self.client.onChatError(ChatError.Chat_message_is_overflow)
            return False
        return True



class MessageInfoEnum:

    message = "message"
    photoIndex = "photoIndex"
    name = "name"
    level = "level"
    vipLevel = "vipLevel"
    sendTime = "sendTime"
    clubPosition = "clubPosition"























