# -*- coding: utf-8 -*-
import KBEngine
import gc
from KBEDebug import *
from common.skill.SkillModuleMain import SkillModuleMain


class Card(KBEngine.Entity,SkillModuleMain):

#========================KBE方法=================================================
    """
    卡牌
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        SkillModuleMain.__init__(self)
        # print("Cell::Card.__init__")

        # DEBUG_MSG(str(type(self.baseProp)))
        for k, v in self.baseProp.items():
            # DEBUG_MSG("card   k  " + str(k) + "       v  " + str(v))
            self.__setattr__(k, v)

        self.totalAttackValue = 0.0
        self.totalDefendValue = 0.0
        self.totalControllValue = 0.0
        # 上一轮的攻击者
        self.preAttackId = -1
        # 当前进攻者ID
        self.curAttackID = -1
        # 上一轮的防守者 列表
        self.preDefIds = -1
        # 上一轮是否完美助攻的射门系数
        self.o1 = 1

    def onTimer(self, tid, userArg):

        """
        KBEngine method.
        引擎回调timer触发
        """
        ERROR_MSG("ontimer" + str(userArg))
        DEBUG_MSG(tid, userArg)

    def onDestroy(self):

        # ERROR_MSG("card   onDestroy       " + str(sys.getrefcount(self)))
        # del gc.garbage[:]

        # ERROR_MSG(gc.get_referrers(self))
        """
        KBEngine method.
        """
        pass


    def onSetBaseProp(self,baseProp):

        for k, v in self.baseProp.items():
            # DEBUG_MSG("card   k  " + str(k) + "       v  " + str(v))

            self.__setattr__(k, v)


#========================房间内事件=================================================



    def onEnter(self, entityMailbox):
        """
        进入场景
        """
        print("Cell::Room.onEnter")

    def onLeave(self, entityID):
        """
        离开场景
        """
        print("Cell::Room.onLeave")

    def onSpaceGone(self):
        self.destroy()

    def getShoot(self):
        return (self.shoot + self.shootSkillValue) * self.shootSkillPer


    def getDefend(self):
        return (self.defend + self.defendSkillValue) * self.defendSkillPer


    def getPassBall(self):
        return (self.passBall + self.passballSkillValue) * self.passballSkillPer


    def getTrick(self):
        return (self.trick + self.trickSkillValue) * self.trickSkillPer


    def getReel(self):
        return (self.reel + self.reelSkillValue) * self.reelSkillPer


    def getSteal(self):
        return (self.steal + self.stealSkillValue) * self.stealSkillPer


    def getControll(self):
        return (self.controll + self.controllSkillValue) * self.controllSkillPer


    def getKeep(self):
        return (self.keep + self.keepSkillValue) * self.keepSkillPer

