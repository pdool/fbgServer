# -*- coding: utf-8 -*-
import importlib
import time
import datetime

import gc
import guildConfig
import util
from CommonEnum import ActionTypeEnum
from GMConfig import GMConfig
from part.guild.GuildModule import GuildModule
import CommonConfig
import vipConfig
import gameShopConfig
from KBEDebug import *
from part.footballTeam.DiamondContainer import DiamondContainer
from part.footballTeam.EquipsContainer import EquipsContainer
from part.footballTeam.GiftContainer import GiftContainer
from part.footballTeam.MaterialContainer import MaterialContainer
from part.footballTeam.PiecesContainer import PiecesContainer
from part.footballTeam.UseContainer import UseContainer
from part.SlevelModule import SlevelModule
from part.BagModule import BagModule
from part.BodyPowerModule import BodyPowerModule
from part.CardMgrModule import CardMgrModule
from part.ChatModule import ChatModule
from part.FriendModule import FriendModule, FriendInfoKey, FriendOnlineState
from part.LotteryModule import LotteryModule
from part.MailsModule import MailsModule
from part.PropMgrModule import PropMgrModule
from part.ShopModule import ShopModule
from part.CloneModule import CloneModule
from part.EquipModule import EquipModule
from part.MentalityModule import MentalityModule
from part.StrikeModule import StrikeModule
from part.InheritModule import InheritModule
from part.AbilityModule import AbilityModule
from part.BabyModule import BabyModule
from part.FormationModule import FormationModule
from part.GameShopModule import GameShopModule
from part.RankModule import RankModule
from part.LevelUpModule import LevelUpModule
from part.MoneyModule import MoneyModule
from part.OfficialModule import OfficialModule
from part.ArenaModule import ArenaModule
from part.SkillModule import SkillModule
from part.WorldBossModule import WorldBossModule
from badWords import badWords
from part.guild.GuildTask import GuildTask
from part.league.LeagueModule import LeagueModule

import TimerDefine


# 使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用


class Avatar(KBEngine.Proxy,
             MailsModule,
             LotteryModule,
             ShopModule,
             FriendModule,
             BodyPowerModule,
             ChatModule,
             BagModule,
             CardMgrModule,
             DiamondContainer,
             EquipsContainer,
             GiftContainer,
             MaterialContainer,
             PiecesContainer,
             UseContainer,
             PropMgrModule,
             CloneModule,
             EquipModule,
             SlevelModule,
             MentalityModule,
             StrikeModule,
             InheritModule,
             AbilityModule,
             BabyModule,
             GuildModule,
             GuildTask,
             FormationModule,
             GameShopModule,
             RankModule,
             LevelUpModule,
             MoneyModule,
             OfficialModule,
             ArenaModule,
             SkillModule,
             WorldBossModule,
             LeagueModule
             ):
    """
    角色实体
    """

    def __init__(self):
        KBEngine.Proxy.__init__(self)
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, '__init__'):
                c.__init__(self)

        # MailsModule.__init__(self)
        # ShopModule.__init__(self)

        self.accountEntity = None

    # 创建角色时调用
    def onCreateRole(self):
        # 初始化替补数量
        self.initBench()
        # 加入等级排行
        self.updateLevelValueRank()
        # 加入财富排行
        self.updateMoneyValueRank()
        # 加入官职排行
        self.updateOfficalValueRank()
        # 加入竞技场排行
        self.onAddArenaRank()
        # 购买竞技次数
        self.buyArenaTimes = vipConfig.VipConfig[self.vipLevel]["buyArenaTimes"]
        # 竞技次数
        self.arenaTimes = CommonConfig.CommonConfig[6]["value"]



        # 解锁章节
        self.onCreateRoleUnlockChapter()
    # 上线
    def onEntitiesEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        # cls = Avatar.__bases__
        # for c in cls:
        #
        #     c().onEntitiesEnabled()

        # 知识点，绑定方法，非绑定方法 父类列表

        self.onGetFromLastOutLinesDays()
        DEBUG_MSG("self.roleId---------------------" + str(self.roleId))
        onlineSet = KBEngine.globalData["Onlines"]
        onlineSet.add(self.databaseID)
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, 'onEntitiesEnabled'):
                c.onEntitiesEnabled(self)

        self.client.onEnterScene()

        playerInfo = {}
        playerInfo[FriendInfoKey.DBID] = self.databaseID
        playerInfo[FriendInfoKey.photoIndex] = self.photoIndex
        playerInfo[FriendInfoKey.name] = self.name

        playerInfo[FriendInfoKey.level] = self.level
        playerInfo[FriendInfoKey.clubName] = self.club
        playerInfo[FriendInfoKey.fightValue] = self.fightValue
        playerInfo[FriendInfoKey.vipLevel] = self.vipLevel
        playerInfo[FriendInfoKey.formation] = self.formation
        playerInfo[FriendInfoKey.onlineState] = FriendOnlineState.online

        KBEngine.globalData["PlayerMgr"].playerLogin(self, self.databaseID, playerInfo)


        # --------------------------------------------------------------------------------------------
        #                              属性列表
        # --------------------------------------------------------------------------------------------

        self.initProp()

    def destroySelf(self):
        """
        """
        if self.client is not None:
            ERROR_MSG("self.client is not None ==================================================")
            return



        # 如果帐号ENTITY存在 则也通知销毁它
        if self.accountEntity != None:
            self.accountEntity.activeAvatar = None
            # self.accountEntity = None

            self.accountEntity.destroy()

            ERROR_MSG("------------ self.accountEntity.destroy()")
            # if time.time() - self.accountEntity.relogin > 1:
            #     self.accountEntity.activeAvatar = None
            #     self.accountEntity.destroy()
            self.accountEntity = None
            # else:
            #     DEBUG_MSG("Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))

        # 销毁base
        if self.cell is not None:
            # self.destroyCellEntity()
            self.cellLoseReason = "clientDeath"
            ERROR_MSG("cellLoseReason ==================================================")
            return
        self.onTimerSaveBag()
        self.destroy()

        ERROR_MSG("avatar  destroy ==================================================")

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        if hasattr(self, "cellLoseReason") and self.cellLoseReason == "clientDeath":
            self.destroy()
            return

    def onDestroy( self ):

        # refs = gc.get_referents(self)
        #
        # ERROR_MSG("  avatar   onDestroy    " + refs.__str__())
        pass




    def initProp(self):
        self.initMail()  # 初始化邮件

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if TimerDefine.Time_destroy_avatar == userArg:
            self.destroySelf()

        # GameObject.onTimer(self, tid, userArg)
        # 调用子类的onTimer函数
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, 'onTimer'):
                c.onTimer(self, tid, userArg)

    # 下线
    def onClientDeath(self):
        """
        KBEngine method.
        entity丢失了客户端实体
        """
        self.addTimer(5, 5, TimerDefine.Time_destroy_avatar)
        self.lastTime = str(datetime.datetime.now().hour) + "," + str(datetime.datetime.now().minute) + "," + str(
            datetime.datetime.now().second)

        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
        # 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
        # 这段时间内客户端短连接登录则会激活entity
        # self._destroyTimer = self.addTimer(1, 0, SCDefine.TIMER_TYPE_DESTROY)
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, 'onClientDeath'):
                c.onClientDeath(self)

        self.logoutTime = util.getCurrentTime()

        DEBUG_MSG("--------logoutTime   ----------------" + str(self.logoutTime))

        playerInfo = {}

        playerInfo[FriendInfoKey.DBID] = self.databaseID
        playerInfo[FriendInfoKey.photoIndex] = self.photoIndex
        playerInfo[FriendInfoKey.name] = self.name

        playerInfo[FriendInfoKey.level] = self.level
        playerInfo[FriendInfoKey.clubName] = self.club
        playerInfo[FriendInfoKey.fightValue] = self.fightValue
        playerInfo[FriendInfoKey.vipLevel] = self.vipLevel
        playerInfo[FriendInfoKey.onlineState] = self.logoutTime
        playerInfo[FriendInfoKey.formation] = self.formation

        KBEngine.globalData["PlayerMgr"].playerOffline(self.databaseID, playerInfo)

        baby = KBEngine.entities.get(self.babyID)
        if baby is not None:
            baby.destroyBaby()

        for id in self.cardIDList:
            card = KBEngine.entities.get(id)
            if card is None:
                continue
            card.destroyCard()

        if hasattr(self, "spaceMb") and self.spaceMb is not None and self.spaceMb.isDestroyed is not True:
            self.spaceMb.destroyClone()


        self.destroySelf()

    # 获取离上次下线过了几天
    def onGetFromLastOutLinesDays(self):
        if len(self.lastTime) == 0:
            return
        hour = self.lastTime.split(",")[0]
        mintue = self.lastTime.split(",")[1]
        second = self.lastTime.split(",")[2]
        offset = 86400 - (int(hour) * 3600 + int(mintue) * 60 + int(second))
        days = 0
        period = util.getCurrentTime() - int(self.logoutTime)
        if period > offset:
            days = 1 + (period - offset) // 86400
        if days > 0:
            for Item in self.gameShopItemList:
                config = gameShopConfig.gameShopConfig[Item["itemID"]]
                Item["limitTimes"] = config["limitTimes"]
            # 购买竞技次数
            self.buyArenaTimes = int(vipConfig.VipConfig[self.vipLevel]["buyArenaTimes"])
            # 竞技次数
            self.arenaTimes = int(CommonConfig.CommonConfig[6]["value"])
            self.isPrompt = 0
            self.isCanEncourage = 0
            self.officialReward = 0
            self.buyLinePower = 0
            self.updateforPermissionInfo()
        ERROR_MSG("-------have  "+str(days)+"  days not enter game-------")
        return days



    def onClientGetCell(self):
        """
        KBEngine method.
        客户端已经获得了cell部分实体的相关数据
        """
        INFO_MSG("Avatar[%i].onClientGetCell:%s" % (self.id, self.client))

    def onDestroyTimer(self):
        DEBUG_MSG("Avatar::onDestroyTimer: %i" % (self.id))
        self.destroySelf()

    def onPlayerMgrCmd(self, funcName, argsDict):

        DEBUG_MSG("------onPlayerMgrCmd------" + funcName)
        if funcName == "":
            return

        func = getattr(self, funcName)

        func(argsDict)

        if funcName != "":
            DEBUG_MSG("call me onPlayerMgrCmd")

    def onClientGM(self, gmStr):
        gmList = gmStr.split(" ")
        if gmList[0] == "euro":
            self.rechargeEuro(int(gmList[1]))
            return
        if gmList[0] == "blackMoney":
            self.blackMoney = self.blackMoney + int(gmList[1])
            return
        if gmList[0] == "level":
            self.level = int(gmList[1])
            card = KBEngine.entities.get(self.cardID)
            card.level = int(gmList[1])
            self.client.onUpdateCardInfo(self.UpdateBallerInfo(card))
            self.updateLevelValueRank()
            return
        if gmList[0] == "guildFunds":
            self.guildFunds = self.guildFunds + int(gmList[1])

        if gmList[0] == "fame":
            self.fame = self.fame + int(gmList[1])

        if hasattr(self, gmList[0]):
            attrType = type(getattr(self, gmList[0]))
            value = attrType(gmList[1])
            setattr(self, gmList[0], value)
        else:
            DEBUG_MSG("avatar don't have the " + gmList[0])

    def reloadc(module):
        importlib.reload(module)
        KBEngine.reloadScript()

    def onClientGmAddItem(self,itemID,count):
        self.putItemInBag(itemID, count)

    def onClientGmAddAll(self):
        self.diamond = 99999999
        self.addRmb(99999999)
        self.rechargeEuro(99999999)

    def onClientChangeSolgan(self, slogan):
        slogan = self.replaceBadWords(slogan)
        self.slogan = slogan

    # 是否有脏话
    def replaceBadWords(self, message):
        for word in badWords:
            message = message.replace(word, '*')
        return message

    # 是否有脏话
    def checkHasBadWords(self, message):
        for word in badWords:
            if message.find(word) != -1:
                return True
        return False

    def onCmdGetPlayerInfo(self, arg):
        avatar = arg["playerMB"]
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
        avatar.client.onGetPlayerInfo(param)

    def onClientGetPlayerInfo(self, dbid):
        def agreeCB(avatar, dbid, wasActive):
            if avatar != None:
                param = {
                    "fightValue": avatar.fightValue,
                    "vipLevel": avatar.vipLevel,
                    "slogan": avatar.slogan,
                    "club": avatar.club,
                    "camp": avatar.camp,
                    "isRobot": 0,
                    "playerName": avatar.name,
                    "dbid": avatar.databaseID,
                    "offical": avatar.officialPosition,
                    "level": avatar.level,
                    "guildName": avatar.guildName,
                }
                self.client.onGetPlayerInfo(param)
                if wasActive == 0:
                    avatar.destroySelf()
            else:
                ERROR_MSG("---------Cannot add unknown player:-------------")

        KBEngine.createBaseFromDBID("Avatar", dbid, agreeCB)

    def onRoomEndResult(self,avatarAID,aScore,avatarBID,bScore):

        ERROR_MSG(util.printStackTrace("onRoomEndResult "))

        if self.inActionType == ActionTypeEnum.action_clone:
            self.judgeInFootBallFeast(avatarAID,aScore,avatarBID,bScore)
        elif self.inActionType == ActionTypeEnum.action_world_boss:
            self.onWorldBossEndResult(avatarAID,aScore,avatarBID,bScore)
        elif self.inActionType == ActionTypeEnum.official_promotion:
            self.onOfficialEndResult(avatarAID,aScore,avatarBID,bScore)
        elif self.inActionType == ActionTypeEnum.action_arena:
            self.onArenaEndResult(avatarAID,aScore,avatarBID,bScore)
        elif self.inActionType == ActionTypeEnum.league_clone:
            self.onLeagueEndResult(avatarAID, aScore, avatarBID, bScore)
        elif self.inActionType == ActionTypeEnum.league_player:
            self.onLeagueEndResult(avatarAID, aScore, avatarBID, bScore)
        self.inRoom = 0



if __name__ == "__main__":
    a = Avatar()
    m = a.replaceBadWords("习近平   xxxxx")
    print(m)
