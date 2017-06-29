# -*- coding: utf-8 -*-
import KBEngine
import random, math
import time
import GlobalDefine
from KBEDebug import *
from modules.ArenaModule import ArenaModule
from modules.BabyModule import BabyModule
from modules.BagModule import BagModule
from modules.BodyPowerModule import BodyPowerModule
from modules.CardMgrModule import CardMgrModule
from modules.ChatModule import ChatModule
from modules.CloneModule import CloneModule
from modules.EquipModule import EquipModule
from modules.FormationModule import FormationModule
from modules.FriendModule import FriendModule
from modules.GameShopModule import GameShopModule
from modules.GuildModule import GuildModule
from modules.InheritModule import InheritModule
from modules.LotteryModule import LotteryModule
from modules.MailsModule import MailsModule
from modules.MentalityModule import MentalityModule
from modules.OfficialModule import OfficialModule
from modules.PiecesModule import PiecesModule
from modules.RankModule import RankModule
from modules.ShopModule import ShopModule
from modules.SkillModule import SkillModule
from modules.SlevelModule import SlevelModule
from modules.WorldBossModule import WorldBossModule


class Avatar(KBEngine.Entity,
             ArenaModule,
             BabyModule,
BagModule,
BodyPowerModule,
CardMgrModule,
ChatModule,
CloneModule,
EquipModule,
FormationModule,
FriendModule,
GameShopModule,
GuildModule,
InheritModule,
LotteryModule,
MailsModule,
MentalityModule,
OfficialModule,
PiecesModule,
RankModule,
ShopModule,
SkillModule,
SlevelModule,
WorldBossModule,
             ):
    def __init__(self):
        KBEngine.Entity.__init__(self)

        cls = Avatar.__bases__
        for c in cls:
            if hasattr(c, '__init__'):
                c.__init__(self)


    def onEnterSpace(self):
        """
        KBEngine method.
        这个entity进入了一个新的space
        """
        DEBUG_MSG("%s::onEnterSpace: %i" % (self.__class__.__name__, self.id))

    def onLeaveSpace(self):
        """
        KBEngine method.
        这个entity将要离开当前space
        """
        DEBUG_MSG("%s::onLeaveSpace: %i" % (self.__class__.__name__, self.id))

    def onBecomePlayer( self ):
        """
        KBEngine method.
        当这个entity被引擎定义为角色时被调用
        """
        DEBUG_MSG("%s::onBecomePlayer: %i" % (self.__class__.__name__, self.id))

    def onJump(self):
        """
        defined method.
        玩家跳跃
        """
        pass

    def update(self):
        pass

    def onOperateSuc(self,str):
        pass

    def onGiftError(self,errorCode):
        pass

    def onCardFightValueChange(self,p1,p2):
        pass
    def onGetPlayerInfo(self,playerInfo):
        pass

    def onAISelectError(self):
        pass

    def   onEnterScene(self):
        pass