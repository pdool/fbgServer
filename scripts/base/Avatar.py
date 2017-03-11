# -*- coding: utf-8 -*-
import importlib

import util
from GMConfig import GMConfig

from KBEDebug import *
from part.SlevelModule import SlevelModule
from part.BagModule import BagModule
from part.BodyPowerModule import BodyPowerModule
from part.CardMgrModule import CardMgrModule
from part.ChatModule import ChatModule
from part.FriendModule import FriendModule,FriendInfoKey,FriendOnlineState
from part.LotteryModule import LotteryModule
from part.MailsModule import MailsModule
from part.PropMgrModule import PropMgrModule
from part.ShopModule import ShopModule
from part.footballTeam.DiamondModule import DiamondModule
from part.footballTeam.EquipsModule import EquipsModule
from part.footballTeam.GiftModule import GiftModule
from part.footballTeam.MaterialModule import MaterialModule
from part.footballTeam.PiecesModule import PiecesModule
from part.footballTeam.UseModule import UseModule
from part.CloneModule import CloneModule
from part.EquipModule import EquipModule
from part.MentalityModule import MentalityModule
from part.StrikeModule import StrikeModule
from part.InheritModule import InheritModule
from part.AbilityModule import AbilityModule

import TimerDefine

#使用技巧 先放在根级目录。，调好之后拖走，编辑器自动组织引用
class Avatar(KBEngine.Proxy,
             MailsModule,
             LotteryModule,
             ShopModule,
             FriendModule,
             BodyPowerModule,
             ChatModule,
             BagModule,
             CardMgrModule,
             DiamondModule,
             EquipsModule,
             GiftModule,
             MaterialModule,
             PiecesModule,
             UseModule,
             PropMgrModule,
             CloneModule,
             EquipModule,
             SlevelModule,
             MentalityModule,
             StrikeModule,
             InheritModule,
             AbilityModule,
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
        playerInfo[FriendInfoKey.onlineState] = FriendOnlineState.online
        KBEngine.globalData["PlayerMgr"].playerLogin(self,self.databaseID,playerInfo)

        self.addTimer(5, 5, TimerDefine.Time_destroy_avatar)
        # --------------------------------------------------------------------------------------------
        #                              属性列表
        # --------------------------------------------------------------------------------------------

        self.initProp()

    def destroySelf(self):
        """
        """
        if self.client is not None:
            return

        if self.cell is not None:
            self.destroyCellEntity()
            return

        # 如果帐号ENTITY存在 则也通知销毁它
        if self.accountEntity != None:

            self.accountEntity.activeAvatar = None
            # self.accountEntity = None

            self.accountEntity.destroy()

            DEBUG_MSG("------------ self.accountEntity.destroy()")
            # if time.time() - self.accountEntity.relogin > 1:
            #     self.accountEntity.activeAvatar = None
            #     self.accountEntity.destroy()
            #     self.accountEntity = None
            # else:
            #     DEBUG_MSG("Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))

        # 销毁base

        self.destroy()

        DEBUG_MSG("destroy ==================================================")


    def initProp(self):
        self.initMail()#初始化邮件

    #--------------------------------------------------------------------------------------------
    #                              Callbacks
    #--------------------------------------------------------------------------------------------
    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
        if TimerDefine.Time_destroy_avatar == userArg:
            self.destroySelf()

        # GameObject.onTimer(self, tid, userArg)
        # 调用子类的onTimer函数
        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, 'onTimer'):
                c.onTimer(self,tid, userArg)

    # 下线
    def onClientDeath(self):
        """
        KBEngine method.
        entity丢失了客户端实体
        """
        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
        # 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
        # 这段时间内客户端短连接登录则会激活entity
        # self._destroyTimer = self.addTimer(1, 0, SCDefine.TIMER_TYPE_DESTROY)
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

        KBEngine.globalData["PlayerMgr"].playerOffline(self.databaseID,playerInfo)


        for id in self.cardIDList:
            card = KBEngine.entities.get(id)
            if card is None:
                continue
            card.destroyCard()


        if hasattr(self,"spaceMb") and self.spaceMb is not None and self.spaceMb.isDestroyed is not True:
            self.spaceMb.destroyClone()
        self.destroySelf()


    def onClientGetCell(self):
        """
        KBEngine method.
        客户端已经获得了cell部分实体的相关数据
        """
        INFO_MSG("Avatar[%i].onClientGetCell:%s" % (self.id, self.client))

    def onDestroyTimer(self):
        DEBUG_MSG("Avatar::onDestroyTimer: %i" % (self.id))
        self.destroySelf()

    def onPlayerMgrCmd(self,funcName,argsDict):

        DEBUG_MSG("------onPlayerMgrCmd------" + funcName)
        if funcName == "":
            return

        func = getattr(self, funcName)

        func(argsDict)

        if funcName == "":
            DEBUG_MSG("call me onPlayerMgrCmd")


    def onClientGM(self,gmStr):
        gmList = gmStr.split(" ")
        DEBUG_MSG("gm cmd is : " + gmStr)

        if hasattr(self,gmList[0]):
            attrType = type(getattr(self,gmList[0]))
            value = attrType(gmList[1])
            setattr(self,gmList[0],value)
        else:
            DEBUG_MSG("avatar don't have the " + gmList[0])

    def reloadc(module):
        importlib.reload(module)
        KBEngine.reloadScript()

    def onClientGmAddAll(self):

        self.diamond = 9999999999
        self.addRmb(99999999)
        self.euro = 999999999
        for k ,v in GMConfig.items():
            self.putItemInBag(k,v["itemCountCount"])


