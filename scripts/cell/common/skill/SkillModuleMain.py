# -*- coding: utf-8 -*-
import KBEngine
import skillConfig
import skillMainConfig
import util
from CommonEnum import PlayerOp
from KBEDebug import ERROR_MSG

from cardsConfig import cardsConfig
from common.skill.BufferModule import BufferModule
from common.skill.SkillConditionModule import SkillConditionModule, ConditionEnum
from common.skill.SkillEffectModule import SkillEffectModule
from common.skill.SkillTargetModule import SkillTargetModule

__author__ = 'chongxin'

__createTime__ = '2017年3月15日'

"""
技能模块
(us 己方 enemy 对手  self 自身)
"""


class SkillModuleMain(SkillConditionModule, SkillTargetModule, SkillEffectModule, BufferModule):
    def __init__(self):

        SkillConditionModule.__init__(self)
        SkillTargetModule.__init__(self)
        SkillEffectModule.__init__(self)
        BufferModule.__init__(self)

        self.resetRoundData()

        print(" Skill module")

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
    def useSkill(self, skillID,result):

        if skillID == 0:
            # 没配技能
            return
        skillConMap = skillMainConfig.SkillMain[skillID]
        condition = skillConMap["condition"]

        check = self.checkCondition(condition, result)
        ERROR_MSG("   condition  is  " + str(condition) + "  result  is   " + str(result) + "  check is  " + str(check))
        # 验证不通过
        if check is False:
            return

        subSkillTuple = skillConMap["subSkills"]

        ERROR_MSG("subSkills" + subSkillTuple.__str__())

        for subSkillID in subSkillTuple:
            subSkillID = subSkillID * 100 + 1
            subSkillConMap = skillConfig.SkillConfig[subSkillID]
            conditon = subSkillConMap["condition"]
            # 注意修改result 为112
            if result != conditon:
                continue

            ERROR_MSG("subSkillID    is " + str(subSkillID) + "   " + conditon.__str__())

            usePercent = subSkillConMap["triggerPer"]

            if self.checkTriggerPer(usePercent) is False:
                continue
            ERROR_MSG("target  type is " + str(subSkillConMap["target"]))
            targetList = self.filterTarget(subSkillConMap["target"])
            self.addBuffer(targetList, subSkillID)

        #
        return True

    # 检查触发的概率
    def checkTriggerPer(self,percent):

        p = util.randInHundred()
        print(p)
        if percent >= p:
            return True
        return False

    def afterRound(self, result):
        if result > ConditionEnum.con_result_None:
            self.bufferEffect(result)
    #
    # # 队友进攻时可施放，使用后，如果该轮次射门未进，则技能持有者进行一次补射。补射的威力系数固定（公式中的距离威力系数，暂设为0
    # # .6），且只有守门员一个防守者。
    # def useSkill1004(self,result):
    #     if result != ConditionEnum.con_result_shoot_succ:
    #         return
    #     room = KBEngine.entities.get(self.roomID)
    #     # 补射
    #     room.reShootCardId = self.id
    #     room.endRound = False
    #     room.onCmdSelectSkill(PlayerOp.shoot)
    #     # room.
    #
    #     pass
    #
    # # 50%几率直接消耗对方一回合，50%几率自己吃到黄牌
    # def useSkill1014(self,result):
    #     if result != ConditionEnum.con_result_None:
    #         return
    #
    #     p = util.randInHundred()
    #     # 消耗对方一个回合
    #     if p < 50:
    #         self.addEffect23(None,None,None,[])
    #     else:
    #         self.addEffect18(None,None,None,[self.id])
    # # 门柱保命（主\防守回合）：使用技能的3个防守回合内，未能扑出的球（攻守判定为进球），有n%几率打在门柱上。3回合内击中门柱一次后失效
    # def useSkill103601(self,result,buffer):
    #     if result != ConditionEnum.con_result_shoot_succ:
    #         return
    #     skillConMap = skillConfig.SkillConfig[1003601]
    #
    #     conditonTupe = skillConMap["condition"]
    #
    #     for condition in conditonTupe:
    #         check = self.checkCondition(condition, result)
    #         ERROR_MSG(
    #             "   condition  is  " + str(condition) + "  result  is   " + str(result) + "  check is  " + str(check))
    #         if check is False:
    #             return
    #
    #     usePercent = skillConMap["triggerPer"]
    #     if self.checkTriggerPer(usePercent) is False:
    #         return
    #     # 触发技能
    #     else:
    #         # 修改射门结果为失败
    #         room = KBEngine.entities.get(self.roomID)
    #         room.roundResult = ConditionEnum.con_result_shoot_fail
    #         buffer["lastRound"] = 0




if __name__ == '__main__':

    # checkTriggerPer(50)
    pass



















