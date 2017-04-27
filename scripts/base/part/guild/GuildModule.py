# -*- coding: utf-8 -*-
from ErrorCode import GuildModuleError
import guildConfig
import util
from KBEDebug import *

__author__ = 'chongxin'
__createTime__  = '2017年3月30日'
"""
公会模块
"""

class GuildModule:
    # 玩家上线
    def onEntitiesEnabled(self):
        # 刷新在线状态
        self.changeOnlineState(1)
    #     玩家下线
    def onClientDeath(self):
        self.changeOnlineState(util.getCurrentTime())




    # def onTimer(self, id, userArg):
    #     if userArg == TimerDefine.Timer_reset_baller_addInfo:
    #     pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    # 客户端根据阵营请求公会列表
    def onClientGuildList(self):
        argMap = {
            "camp": self.camp,
            "playerMB": self
        }

        self.client.onApplyGuildIDList(self.applyGuildList)
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdGuildList", argMap)
        pass

    # 创建公会
    def onClientCreateGuild(self,guildName,introduction):
        # 1、已经加入公会
        if self.guildDBID != 0:
            self.client.onGuildError(GuildModuleError.Guild_already_in_guild)
            return

        nameLen = len(guildName)
        config = guildConfig.GuildConfig[1]

        # 2、验证名字长度
        if nameLen < config["nameLenMin"] or nameLen > config["nameLenMax"]:
            self.client.onGuildError(GuildModuleError.Guild_name_error)
            return

        # 3、验证非法字符
        if self.checkHasBadWords(guildName):
            self.client.onGuildError(GuildModuleError.Guild_name_error)
            return

        # 4、验证简介
        if self.checkHasBadWords(introduction):
            self.client.onGuildError(GuildModuleError.Guild_introduction_error)
            return

        # 5、验证钻石
        if self.diamond < config["createNeedDiamond"]:
            self.client.onGuildError(GuildModuleError.Guild_diamond_not_enough)
            return

        self.diamond = self.diamond - config["createNeedDiamond"]
        guildMgr = KBEngine.globalData["GuildMgr"]

        argMap = {
            "playerMB"          : self,
            "playerDBID"        : self.databaseID,
            "playerLevel"       : self.level,
            "officalPosition"   : self.officalPosition,
            "playerName"        : self.name,
            "camp"               : self.camp,
            "guildName"         : guildName,
            "introduction"      : introduction,
        }

        guildMgr.onCmd("onCmdCreateGuild",argMap)

    # 获得公会信息
    def onClientGetGuildInfo(self):
        guildDBID = self.guildDBID

        if guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_has_not_join)
            return

        argMap = {
            "playerMB"      : self,
            "guildDBID"     :guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGetGuildInfo",argMap)

    # 获取公会副队长列表及简介
    def onClientGetViceIntroduce(self,guildID):
        argMap = {
            "playerMB": self,
            "guildDBID": guildID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGetGuildViceInfo", argMap)


    # 获取公会成员信息
    def onClientGetGuildMember(self):
        guildDBID = self.guildDBID

        if guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_has_not_join)
            return

        argMap = {
            "playerMB": self,
            "guildDBID": guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdGetGuildMember", argMap)


    # 获取公会申请人列表信息
    def onClientGetGuildApply(self):
         guildDBID = self.guildDBID
         guildPower = self.guildPower

         if guildDBID == 0:
             self.client.onGuildError(GuildModuleError.Guild_has_not_join)
             return

         argMap = {
             "playerMB": self,
             "guildDBID": guildDBID,
             "guildPower": guildPower
         }
         guildMgr = KBEngine.globalData["GuildMgr"]



         guildMgr.onCmd("onCmdGuildApplyList", argMap)

    # 申请加入公会
    def onClientApplyJoinGuild(self,guildDBID):
        # 1、已经加入公会
        if self.guildDBID != 0:
            self.client.onGuildError(GuildModuleError.Guild_already_in_guild)
            return

        # 已经申请了
        if guildDBID in self.applyGuildList:
            self.client.onGuildError(GuildModuleError.Guild_already_apply)
            return
        argMap = {
            "playerMB"          :  self,
            "guildDBID"         :  guildDBID,
            "playerDBID"        : self.databaseID,
            "playerLevel"       : self.level,
            "officalPosition"   : self.officalPosition,
            "playerName"        : self.name,
            "camp"               : self.camp,
        }
        self.applyGuildList.append(guildDBID)
        guildMgr = KBEngine.globalData["GuildMgr"]

        self.client.onApplyGuildIDList(self.applyGuildList)

        guildMgr.onCmd("onCmdApplyJoinGuild",argMap)

    #  离开公会 TODO: 会长检查
    def onClientLeaveGuild(self):
        # 1、已经加入公会
        if self.guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_not_in_guild)
            return

        guildMgr = KBEngine.globalData["GuildMgr"]

        argMap = {
            "playerMB"          :  self,
            "guildDBID"         :  self.guildDBID,
            "playerDBID"        : self.databaseID,
        }
        guildMgr.onCmd("onCmdLeaveGuild",argMap)

    # 批准加入公会
    def onClientAgreeJoin(self,applyerDBID):
        argMap = {
            "playerMB"      : self,
            "selfDBID"      : self.databaseID,
            "guildDBID"     : self.guildDBID,
            "applyerDBID"   : applyerDBID,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdAgreeJoin",argMap)

    # 拒绝申请
    def onClientRejectApply(self,applyerDBID):

        argMap = {
            "playerMB": self,
            "guildDBID": self.guildDBID,
            "applyerDBID": applyerDBID,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdRejectApply",argMap)

    # 取消申请
    def onClientCancelApply(self,guildDBID):
        argMap = {
            "playerMB": self,
            "guildDBID": guildDBID,
            "applyerDBID": self.databaseID,
        }
        if guildDBID in self.applyGuildList:
            self.applyGuildList.remove(guildDBID)
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdCancelApply",argMap)
        self.client.onApplyGuildIDList(self.applyGuildList)


    # 查找派系
    def onClientFindCamp(self,guildName):

        if len(guildName) <= guildConfig.GuildConfig[1]["nameLenMin"]:
            self.client.onGuildError(GuildModuleError.Guild_name_error)
            return

        argMap ={
            "keyWord"       : guildName,
            "camp"           : self.camp,
            "playerMB"      : self,
        }

        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdFindCamp",argMap)

    # 修改公告和简介
    def onClientChangeNotice(self,isIntroductionChange,introduction , isNoticeChange,notice):
        argMap = {
            "playerMB"  : self,
            "guildDBID" :self.guildDBID
        }

        if self.guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_has_not_join)
            return
        # 1、验证简介
        if isIntroductionChange == 1 and self.checkHasBadWords(introduction):
            self.client.onGuildError(GuildModuleError.Guild_introduction_error)
            return
        if isIntroductionChange == 1:
            argMap["introduction"] = introduction


        # 2、验证简介
        if isNoticeChange == 1 and self.checkHasBadWords(notice):
            self.client.onGuildError(GuildModuleError.Guild_notice_error)
            return

        if isNoticeChange == 1:
            argMap["notice"] = notice

        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdChangeNotice",argMap)

    # 修改公会名字
    def onClientChangeName(self,guildName):
        config = guildConfig.GuildConfig[1]
        nameLen = len(guildName)
        # 2、验证名字长度
        if nameLen < config["nameLenMin"] or nameLen > config["nameLenMax"]:
            self.client.onGuildError(GuildModuleError.Guild_name_error)
            return

        # 3、验证非法字符
        if self.checkHasBadWords(guildName):
            self.client.onGuildError(GuildModuleError.Guild_name_error)
            return
        needDiamond = config["changeNameDiamond"]
        # 5、验证钻石
        if self.diamond < needDiamond:
            self.client.onGuildError(GuildModuleError.Guild_diamond_not_enough)
            return

        argMap = {
            "playerMB"  : self,
            "guildDBID" : self.guildDBID,
            "guildName" : guildName
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdChangeGuildName",argMap)

    # 踢出玩家
    def onClientKickOut(self,playerDBID):

        argMap = {
            "playerMB"      : self,
            "selfDBID"      : self.databaseID,
            "playerDBID": self.playerDBID,
            "guildDBID"     : self.guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdKickOut", argMap)

    # TODO:接下来的功能

    # 解散公会
    def onClientDismissGuild(self):
        pass

    # 取消解散公会
    def onClientCancelDismiss(self):
        pass

    # 任命
    def onClientAppointPower(self,power):
        pass

    # 弹劾
    def onClientImpeach(self):
        # 1、已经加入公会
        if self.guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_not_in_guild)
            return

        argMap = {
            "guildDBID" : self.guildDBID,
            "selfDBID"  : self.databaseID,
            "playerMB"  : self
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdImpeach", argMap)





    def setGuildDBID(self,argMap):

        # 已经有公会
        if self.guildDBID != 0:

            return

        guildDBID = argMap["guildDBID"]
        power = argMap["power"]
        # 设置公会ID
        self.guildDBID = guildDBID


    def changeOnlineState(self,onlineState):
        if self.guildDBID == 0:
            return

        argMap = {"playerDBID": self.databaseID,
                  "guildDBID" : self.guildDBID,
                  "onlineState": onlineState
                  }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdChangeOnlineState", argMap)



# TODO:登记验证，开关验证
def checkPlayerLevelDeco(func):


    return False


if __name__ == '__main__':

    g = GuildModule()
    g.onClientCreateGuild("戳大叔大婶撒x","吾问无为谓无无无无无无")
    pass



























