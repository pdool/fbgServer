# -*- coding: utf-8 -*-
import datetime
from _ctypes import *
import ArenaReward
import util
import  guildShopConfig


class subMondule():
    def onTimer(self):
      print("subModule")
class  subModule2():
    def onTimer(self):
        print("subModule----2")
class Parent(subModule2,subMondule):
    def onTimer(self):
        cls = Parent.__bases__
        for c in cls:
            if hasattr(c, 'onTimer'):
                c.onTimer(self)
if __name__ == '__main__':

    p = Parent()
    p.onTimer()










