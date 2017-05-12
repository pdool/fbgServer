# -*- coding: utf-8 -*-
import TimerDefine
import guildAppealConfig
from CommonEnum import MailTypeEnum
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

        offset = util.getLeftSecsToWeekEndHMS(24, 0, 0)
        self.addTimer(offset, 7 * 24 * 60 * 60, TimerDefine.Timer_reset_guild_weekDonate)

        dayOffset = util.getLeftSecsToNextHMS(24,0,0)
        self.addTimer(dayOffset,  24 * 60 * 60, TimerDefine.Timer_reset_guild_dayDonate)

        buildOffset = util.getLeftSecsToNextMins(1)
        self.addTimer(buildOffset,60, TimerDefine.Timer_guild_build_upgrade)



    #     玩家下线
    def onClientDeath(self):
        self.changeOnlineState(util.getCurrentTime())



    # def onTimer(self, id, userArg):
    #     if userArg == TimerDefine.Timer_reset_baller_addInfo:
    #     pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------



    # 间隔七天运行
    def onTimer(self, tid, userArg):
        if userArg == TimerDefine.Timer_reset_guild_weekDonate:
            self.clearGuildweekDonate()
        elif userArg == TimerDefine.Timer_reset_guild_dayDonate:
            self.clearGuildDayDonate()
        elif userArg == TimerDefine.Timer_guild_build_upgrade:
            self.checkBuildUpgrade()
            self.checkGuildProtectTime()
        pass



    #客户端根据阵营请求公会列表
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
            self.client.onGuildError(GuildModuleError.Guild_name_has_illegality)
            return

        # 4、验证简介
        if self.checkHasBadWords(introduction):
            self.client.onGuildError(GuildModuleError.Guild_intro_has_illegality)
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
            "guildDBID" :self.guildDBID,
            "selfDBID":self.databaseID,
            "isIntro":isIntroductionChange,
            "introduce":introduction,
            "isNotice":isNoticeChange,
            "notice":notice
        }

        if self.guildDBID == 0:
            self.client.onGuildError(GuildModuleError.Guild_has_not_join)
            return
        # 1、验证简介
        if isIntroductionChange == 1 and self.checkHasBadWords(introduction):
            self.client.onGuildError(GuildModuleError.Guild_intro_has_illegality)
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
            self.client.onGuildError(GuildModuleError.Guild_name_has_illegality)
            return
        needDiamond = config["changeNameDiamond"]
        # 5、验证钻石
        if self.diamond < needDiamond:
            self.client.onGuildError(GuildModuleError.Guild_diamond_not_enough)
            return

        self.diamond = self.diamond - needDiamond
        argMap = {
            "playerMB"  : self,
            "guildDBID" : self.guildDBID,
            "guildName" : guildName,
            "selfDBID"  :self.databaseID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdChangeGuildName",argMap)


    #  公会捐钱

    def onClientDonate(self,euroTime):

        needEuro = euroTime*guildConfig.GuildConfig[1]["euroPer"]
        if self.euro < needEuro:
            self.client.onGuildError(GuildModuleError.Guild_euro_not_enough)
            return

        exchangePer = guildConfig.GuildConfig[1]["contributionPer"]
        donate = euroTime*exchangePer

        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID,
            "euro" : needEuro,
            "donate":donate
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGuildDonate", argMap)

    # 建筑升级
    def onClientBuildUpgrade(self,buildId):

        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "buildID" : buildId,
            "guildDBID": self.guildDBID,
        }

        if self.guildDBID == 0:
            return
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdBuildUpgrade", argMap)

        pass

    # 建筑升级加速
    def onClientBuildSpeed(self,buildID,speedHour):

        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "buildID" : buildID,
            "guildDBID": self.guildDBID,
            "speedHour": speedHour,

        }

        if self.guildDBID == 0:
            return
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdBuildSpeed", argMap)

        pass



    # 清除公会成员周贡献
    def clearGuildweekDonate(self):

        argMap = {
            "playerMB": self,
            "guildDBID" : self.guildDBID
        }
        if self.guildDBID == 0 :
            return
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdClearWeekDonate", argMap)
        pass

    # 清除公会成员日贡献
    def clearGuildDayDonate(self):
        argMap = {
            "playerMB": self,
            "guildDBID": self.guildDBID
        }
        if self.guildDBID == 0:
            return
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdClearDayDonate", argMap)
        pass

    # 检查公会解散时间
    def checkGuildDismiss(self):
        argMap = {
            "playerMB": self,
            "guildDBID": self.guildDBID
        }
        if self.guildDBID == 0:
            return
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdCheckGuildDismiss", argMap)
        pass

    # 检查公会建筑升级
    def checkBuildUpgrade(self):
        argMap = {
            "playerMB": self,
            "guildDBID": self.guildDBID
        }
        if self.guildDBID == 0:
            return
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdCheckBuild", argMap)

    # 检查公会保护时间
    def checkGuildProtectTime(self):
        if self.guildDBID == 0:
            return
        argMap = {
            "playerMB": self,
            "guildDBID": self.guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdCheckProtectTime",argMap)

    # 退出公会
    def onClientQuitGuild(self):
        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdQuitGuild", argMap)


    # 踢出玩家
    def onClientKickOut(self,playerDBID):

        argMap = {
            "playerMB"      : self,
            "playerDBID"    : playerDBID,
            "selfDBID"      : self.databaseID,
            "guildDBID"     : self.guildDBID
        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdKickOut", argMap)

    # TODO:接下来的功能

    # 解散公会
    def onClientDismissGuild(self):
        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdDismissGuild", argMap)

        pass


    # 取消解散公会
    def onClientCancelDismiss(self):
        argMap = {
            "playerMB": self,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdCancelDismiss", argMap)
        pass

    # 任命
    def onClientAppointPower(self,playerDBID,power):
        argMap = {
            "playerMB": self,
            "playerDBID": playerDBID,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID,
            "power"   : power
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdAppointPower", argMap)

        pass
    # 公会转让
    def onClientGuildTransfer(self,playerDBID):
        argMap = {
            "playerMB": self,
            "playerDBID": playerDBID,
            "selfDBID": self.databaseID,
            "guildDBID": self.guildDBID,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGuildTransfer", argMap)

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

    # 发送公会邮件邮件
    def onClientSendGuildMail(self,title, text):
        # 1、检查权限

        # 2、发送邮件
        argMap = {
            "guildDBID" : self.guildDBID,
            "playerMB"  : self,
            "title"     : title,
            "text"      : text,
        }
        guildMgr = KBEngine.globalData["GuildMgr"]
        # 请求公会成员列表
        guildMgr.onCmd("onCmdSendGuildMail", argMap)


    # 响应发送公会邮件
    def onRespSendGuildMail(self,argMap):

        memDBIDList = argMap["memDBIDList"]
        title = argMap["title"]
        text = argMap["text"]

        for dbid in memDBIDList:
            if dbid == self.id:
                continue
            self.sendMail( dbid, MailTypeEnum.Mail_Type_Guild, title, text)




    def setGuildDBID(self,argMap):

        guildDBID = argMap["guildDBID"]
        guildPower = argMap["power"]
        # 设置公会ID
        self.guildDBID = guildDBID
        self.guildPower = guildPower

        self.applyGuildList=[]

        if "guildShopLevel" in argMap:
            guildShopLevel = argMap["guildShopLevel"]
            self.guildShopLevel = guildShopLevel

    #设置申请玩家的申请公会ID列表
    def setApplyGuildDBIDList(self,argMap):

        guildDBID = argMap["guildDBID"]
        for guildId in self.applyGuildList:
            if guildId == guildDBID:
                self.applyGuildList.remove(guildId)



    def changeOnlineState(self,onlineState):
        if self.guildDBID == 0:
            return

        argMap = {"playerDBID": self.databaseID,
                  "guildDBID" : self.guildDBID,
                  "onlineState": onlineState
                  }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdChangeOnlineState", argMap)


    # 公会升级
    def guildUpdate(self):
        if self.guildDBID == 0:
            return

        argMap = {"playerDBID": self.databaseID,
                  "guildDBID": self.guildDBID,
                  "playerMB": self
                  }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdGuildUpdate", argMap)
        pass

    # 公会上诉曝光

    def onClientAppealExposure(self,guildID,appeadID):
        ERROR_MSG("---onClientAppealExposure-appeadID--"+str(guildID))

        if self.guildDBID == 0:
            return
        ERROR_MSG("---onClientAppealExposure-appeadID--"+str(appeadID))

        argMap = {"selfDBID": self.databaseID,
                  "guildDBID": guildID,
                  "playerMB": self,
                  "appeadID":appeadID,

                  }
        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGuildAppealExposure", argMap)

        pass

    # 购买公会保护时间
    def onClientBuyGuildProtect(self,buyHour):

        if self.guildDBID == 0:
            return

        needDiamond = buyHour * guildConfig.GuildConfig[1]["protectPer"]
        if self.diamond < needDiamond :
            self.client.onGuildError(GuildModuleError.Guild_diamond_not_enough)
            return

        self.diamond = self.diamond - needDiamond

        argMap = {"selfDBID": self.databaseID,
                  "guildDBID": self.guildDBID,
                  "playerMB": self,
                  "hour":buyHour
                  }

        guildMgr = KBEngine.globalData["GuildMgr"]
        guildMgr.onCmd("onCmdGuildBuyProtect", argMap)


    # GM 增加公会资金
    def onClientGMAddGuildFunds(self,funds):
        if self.guildDBID == 0:
            return

        argMap = {
                  "guildDBID": self.guildDBID,
                  "funds": funds
                  }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdGMAddGuildFunds", argMap)

        # GM 增加公会声望

    def onClientGMAddGuildReputation(self, reputation):
        if self.guildDBID == 0:
            return

        argMap = {
            "guildDBID": self.guildDBID,
            "reputation": reputation,
            "playerMB": self

        }
        guildMgr = KBEngine.globalData["GuildMgr"]

        guildMgr.onCmd("onCmdGMAddGuildReputation", argMap)



# TODO:登记验证，开关验证
def checkPlayerLevelDeco(func):


    return False


if __name__ == '__main__':

    g = GuildModule()
    g.onClientCreateGuild("戳大叔大婶撒x","吾问无为谓无无无无无无")
    pass



























