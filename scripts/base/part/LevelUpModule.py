# -*- coding: utf-8 -*-
from cardLevelUpgradeConfig import levelIniConfig
from cardLevelUpgradeConfig import cardLevelUpgradeConfig
from ErrorCode import CardMgrModuleError
from KBEDebug import *
__author__ = 'yangh'
"""
主角升级
"""


class LevelUpModule:
    def onEntitiesEnabled(self):
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    # 主角升级
    def levelUp(self, addExp):
        maxLevel = levelIniConfig[0]["maxLevel"]
        currentLevel = self.level
        currentExp = self.exp + addExp
        if currentLevel >= maxLevel:
            self.client.onBallerCallBack(CardMgrModuleError.Card_is_max_level)
            return

        for i in range(currentLevel, maxLevel + 1):
            if i >= maxLevel:
                self.level = maxLevel
                self.exp = cardLevelUpgradeConfig[maxLevel - 1]["maxExp"]
                break
            needExp = cardLevelUpgradeConfig[i]["maxExp"]
            if currentExp < needExp:
                self.level = i
                self.exp = currentExp
                break
        if self.level != currentLevel:
            self.level = currentLevel
            self.updateLevelValueRank()





                # --------------------------------------------------------------------------------------------
                #                              工具函数调用函数
                # --------------------------------------------------------------------------------------------

                # 装备


if __name__ == "__main__":
    print(__file__)
    pass
