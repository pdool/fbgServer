# -*- coding: utf-8 -*-
from _ast import Pass

import KBEngine
import skillConfig
import skillMainConfig
import util
from KBEDebug import ERROR_MSG

from common.skill.BufferModule import BufferModule
from common.skill.SkillConditionModule import SkillConditionModule, ConditionEnum
from common.skill.SkillEffectModule import SkillEffectModule
from common.skill.SkillTargetModule import SkillTargetModule
from common.skill.PassiveSkillModule import PassiveSkillModule

__author__ = 'chongxin'

__createTime__ = '2017年3月15日'

"""
技能模块
(us 己方 enemy 对手  self 自身)
"""


class SkillModuleMain(SkillConditionModule, SkillTargetModule, SkillEffectModule, BufferModule,PassiveSkillModule):
    def __init__(self):

        SkillConditionModule.__init__(self)
        SkillTargetModule.__init__(self)
        SkillEffectModule.__init__(self)
        BufferModule.__init__(self)
        PassiveSkillModule.__init__(self)

        self.initMatchData()
        self.resetRoundData()

    # 初始化全局数据
    def initMatchData(self):
        # 无法参与防守(不计算进攻和防守)
        self.unableDefend = False
        # 免疫负面状态
        self.immuneNegativeBuffer = False
        # 初始怒气10点
        self.anger = 100


    # 重置临时数据
    def resetRoundData(self):
        # =======================基本属性==================
        # 1、射门值、射门值 %
        self.shootSkillPer = 1.0
        self.shootSkillValue = 0
        # 2、传球值、传球值 % 
        self.passballSkillPer = 1.0
        self.passballSkillValue = 0
        # 3、盘带值、盘带值 %
        self.reelSkillPer = 1.0
        self.reelSkillValue = 0
        # 4、控球值、控球值 %（增加控球值效果的技能都是被动，在计算攻守回合数时就要计算进去）
        self.controllSkillPer = 1.0
        self.controllSkillValue = 0
        # 5、防守值、防守值 %
        self.defendSkillPer = 1.0
        self.defendSkillValue = 0
        # 6、拦截值、拦截值 %
        self.trickSkillPer = 1.0
        self.trickSkillValue = 0
        # 7、抢断值、抢断值 % pppp
        self.stealSkillPer = 1.0
        self.stealSkillValue = 0.0
        # 8、守门值、守门值 %
        self.keepSkillPer = 1.0
        self.keepSkillValue = 0.0
        # ==========================计算中间值p======================================
        # 9、射偏率
        self.shootMissSkillPer = 0.0
        # 10、进球率（计算完 （射门值 - 防守值） / 守门值的值）
        self.shootSuccSkillPer = 0.0
        # 11、过人成功率（计算完 （抢断值 - 盘带值） / 抢断基数的值）
        self.breakthroughSkillPer = 0.0
        # 12、完美传球几率（计算完 （传球 - 拦截） / 传球基数的值）
        self.perfectPassballSkillPer = 0.0

        # 14、终结者计算得球概率提升
        self.thirdStepAttackSkillPer = 0.0
        # 15、中间者计算得球概率提升
        self.secondStepAttackSkillPer = 0.0

        self.yellow = 0
        self.red = 0



    # 使用技能（起点）
    def useSkill(self, mainSkillID,skillLevel,result):

        ERROR_MSG("mainSkillID     " + str(mainSkillID))

        if mainSkillID == 0:
            # 没配技能
            return
        skillConMap = skillMainConfig.SkillMain[mainSkillID]
        condition = skillConMap["condition"]
        if mainSkillID != 1035:
            # 检查主技能的使用条件
            check = self.checkCondition(condition, result)
            ERROR_MSG("   condition  is  " + str(condition) + "  result  is   " + str(result) + "  check is  " + str(check))
            # 验证不通过
            if check is False:
                return False


        if mainSkillID == 1009:
            self.useSkill1009(skillLevel,result)
        elif mainSkillID == 1014:
            self.useSkill1014(skillLevel,result)
        elif mainSkillID == 1035:
            self.useSkill1035(result)
        else:

            subSkillTuple = skillConMap["subSkills"]

            ERROR_MSG("subSkills" + subSkillTuple.__str__())

            for subSkillID in subSkillTuple:
                subSkillID = subSkillID * 100 + skillLevel
                subSkillConMap = skillConfig.SkillConfig[subSkillID]
                usePercent = subSkillConMap["triggerPer"]

                ERROR_MSG("target  type is " + str(subSkillConMap["target"]))
                targetList = self.filterTarget(subSkillConMap["target"])


                # 分开单个人触发效果
                for target in targetList:
                    skillID = subSkillID // 10000
                    if skillID == 1036:
                        self.addBuffer(target, subSkillID)
                        continue
                    if skillID == 1015 and  not self.check1015Pos():
                        continue
                    if self.checkTriggerPer(usePercent) is False:
                        continue
                    self.addBuffer(target, subSkillID)

            #
        return True

    # 检查触发的概率
    def checkTriggerPer(self,percent):
        if percent >= 100:
            return True
        p = util.randInHundred()
        if percent >= p:
            return True
        return False

    # 检查可能越位 可能出现从前往后传的情况
    def check1015Pos(self):
        room = KBEngine.entities.get(self.roomID)
        curPart = room.curPart
        if curPart == 3 or curPart == 1:
            return False
        curRoundAtkCoordinate = room.getCurRoundAtkCoordinate(curPart)/10
        nextRoundAtkCoordinate = room.getCurRoundAtkCoordinate(curPart + 1) /10

        if nextRoundAtkCoordinate >= curRoundAtkCoordinate:
            return False
        return True



    def afterRound(self, result):
        if result > ConditionEnum.con_result_None:
            self.bufferEffect(result)





    # 直塞身后（协\攻击回合）：中间轮可发动，50%几率接球者将反越位成功，形成单刀机会；50%几率被直接门将破坏
    def useSkill1009(self,skillLevel,result):
        if result != ConditionEnum.con_result_None:
            return
        if self.checkCondition10(result):
            p = util.randInHundred()
            if p < 50:
            #     单刀
                room = KBEngine.entities.get(self.roomID)
                defender = KBEngine.entities.get(room.defenderID)
                defender.defList[2] = []

                room = KBEngine.entities.get(self.roomID)
                a = KBEngine.entities.get(room.avatarAID)
                b = KBEngine.entities.get(room.avatarBID)

                # 单刀
                if a.typeStr == "Avatar":
                    a.client.onOneOnOne(10090101)
                if b.typeStr == "Avatar":
                    b.client.onOneOnOne()
            else:
                self.addEffect23(10090101, 23, None, None,[self.id])



    #
    # 50%几率直接消耗对方一回合，50%几率自己吃到黄牌
    def useSkill1014(self,skillLevel,result):
        if result != ConditionEnum.con_result_None:
            return

        p = util.randInHundred()
        # 消耗对方一个回合
        if p < 50:
            self.addEffect23(10140101,23,None,None,[self.id])
            ERROR_MSG("useSkill1014    end round "  )
        else:
            self.addEffect18(10140101,18,None,None,[self.id])

            ERROR_MSG("useSkill1014    get yellow card ")



                    #
    # 战术犯规（协\防守回合）：对方单刀时，进行犯规，根据犯规地点判给对方任意球或点球，自己得到黄牌
    def useSkill1035(self, result):
        if result != ConditionEnum.con_result_None:
            return

        room = KBEngine.entities.get(self.roomID)

        if room.defenderID != self.controllerID:
            return

        # 自己得到黄牌
        self.addEffect18(10350101, 18, None,None, [self.id])







if __name__ == '__main__':

    # checkTriggerPer(50)
    pass



















