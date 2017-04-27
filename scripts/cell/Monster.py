# -*- coding: utf-8 -*-
from KBEDebug import *
from common.skill.SkillModuleMain import SkillModuleMain


class Monster(KBEngine.Entity,SkillModuleMain):

#========================KBE方法=================================================
    """
    卡牌
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        SkillModuleMain.__init__(self)
        print("Cell::Monster.__init__")

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        DEBUG_MSG(tid, userArg)

    def onDestroy(self):
        """
        KBEngine method.
        """
        pass


    def onSpaceGone(self):
        self.destroy()


    def getShoot(self):
        return (self.shoot + self.shootSkillValue) *  self.shootSkillPer


    def getDefend(self):
        return (self.defend  + self.defendSkillValue)* self.defendSkillPer


    def getPassBall(self):
        return (self.passBall + self.passballSkillValue) * self.passballSkillPer


    def getTrick(self):
        return (self.trick  + self.trickSkillValue)* self.trickSkillPer


    def getReel(self):
        return (self.reel + self.reelSkillValue) *  self.reelSkillPer


    def getSteal(self):
        return (self.steal  + self.stealSkillValue)*  self.stealSkillPer


    def getControll(self):
        return (self.controll + self.controllSkillValue) * self.controllSkillPer


    def getKeep(self):
        return (self.keep + self.keepSkillValue) * self.keepSkillPer
