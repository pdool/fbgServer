# -*- coding: utf-8 -*-
import random

import Avatar
import TimerDefine
import playerAtkPosition
import positionAttribute
import positionConfig
import util
from CommonEnum import PlayerOp, HalfEnum
from KBEDebug import *
from common.skill.SkillConditionModule import ConditionEnum, PassiveSkillCondition


class Room(KBEngine.Entity):

    #========================KBE方法=================================================
    """
    游戏房间
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)

        self.initProp()

    # 初始化 副本管理的属性
    def initProp(self):
        """
        room管理的全局数据
        """
        self.avatarAID = -1
        self.avatarBID = -1
        # 得分
        self.aScore = 0
        self.bScore = 0

        self.aAnimFinish = False
        self.bAnimFinish = False

        self.aReady = False
        self.bReady = False

        self.aSelect = False
        self.bSelect = False

        # 总的回合次数
        self.totalAttackTimes = 0
        # 当前进攻序列
        self.curAttackIndex = -1

        self.timePeriodList = []
        # 当前控制者(玩家或者副本)
        self.controllerID = 0
        # 当前防守者的控制者
        self.defenderID = 0
        # 当前回合的第几步
        self.curPart = 1
        # 是否结束此轮
        self.endRound = False
        # 怪的攻击序列
        self.bAttackList = []

        self.roundResult = -1

        self.curPartOp = PlayerOp.passball
        # 补射
        self.reShootCardID = -1

        self.half = HalfEnum.first



    # 设置当前两个玩家的ID
    def setRoomControllerID(self,avatarID):
        if self.avatarAID == -1:
            self.avatarAID = avatarID
        else:
            self.avatarBID = avatarID

    # 计算进攻次数
    def __calcAttackTimes(self, aID, bID):

        # A队进攻次数MA=max(round(回合设定基数*(A队攻击系数+B队攻击系数-5)/(A队防御系数+B队防御系数-5)*(A队控球系数)/(A队控球系数+B队控球系数)*(0.1*rand(1)+0.95),0),1)
        roundBase = 12
        seed = random.random()

        a = KBEngine.entities.get(aID)
        b = KBEngine.entities.get(bID)

        attackTimes = max(round(roundBase * (a.totalAttackValue + b.totalAttackValue - 5) / (a.totalDefendValue + b.totalDefendValue - 5) * (a.totalControllValue) / (a.totalControllValue + b.totalControllValue) * (0.1 * seed + 0.95), 0), 1)

        return  int(attackTimes)

    # 计算玩家总的攻击系数 和 防守次数 和控球系数
    """
    A或B队攻击系数=sum（A或B队阵型位置攻击系数）
    A或B队防御系数=sum（A或B队阵型位置防御系数）
    A或B队控球系数=sum（A或B队阵型位置系数*该位置上球员控球属性）
    """
    def __calAtkAndDefendAndControllValue(self,avatarID):
        avartar = KBEngine.entities.get(avatarID)
        if avartar is None:
            return 0,0,0

        attack = 0.0
        defend = 0.0
        controll = 0.0

        for id in avartar.inTeamcardIDList:
            card = KBEngine.entities.get(id)
            pos = card.pos
            posConfig = positionConfig.PositionConfig[pos]
            if posConfig["attackEnable"] == 1:
                attack = attack + posConfig["attack"]
            defend = defend + posConfig["defend"]
            controll = controll +  card.getControll() * posConfig["controll"]

        return  attack,defend,controll

    # # 计算怪的总的攻击系数 和 防守次数 和控球系数
    # def __calMonsterAtkAndDefendAndControllValue(self):
    #     attack = 0.0
    #     defend = 0.0
    #     controll = 0.0
    #     for id in self.inTeamcardIDList:
    #         monster = KBEngine.entities.get(id)
    #         pos = monster.pos
    #         posConfig = positionConfig.PositionConfig[pos]
    #         if posConfig["attackEnable"] == 1:
    #             attack = attack + posConfig["attack"]
    #         defend = defend + posConfig["defend"]
    #         controll = controll + monster.getControll() * posConfig["controll"]
    #
    #     return attack,defend,controll


    """
       计算基础的数据
   """
    def calcBaseData(self):
        avatarA = KBEngine.entities.get(self.avatarAID)
        avatarB = KBEngine.entities.get(self.avatarBID)

        # 玩家总的攻击系数 和 防御系数  和 控球系数
        avatarA.totalAttackValue, avatarA.totalDefendValue, avatarA.totalControllValue = self.__calAtkAndDefendAndControllValue(self.avatarAID)

        # 怪总的攻击系数 和 防御系数 和 控球系数
        avatarB.totalAttackValue, avatarB.totalDefendValue, avatarB.totalControllValue = self.__calAtkAndDefendAndControllValue(self.avatarBID)

        aAttackTimes = self.__calcAttackTimes(self.avatarAID, self.avatarBID)
        bAttackTimes = self.__calcAttackTimes(self.avatarBID, self.avatarAID)

        self.totalAttackTimes = aAttackTimes + bAttackTimes

        if self.half == HalfEnum.first:
            up = 2700
            down = 0
        else:
            up = 5400
            down = 2701

        timePeriodList =  random.sample(range(down,up), self.totalAttackTimes)
        timePeriodList.sort()

        for i in range(1,len(timePeriodList)):
            if timePeriodList[i] - timePeriodList[i-1] < 30:
                timePeriodList[i] = timePeriodList[i-1] + 30

        self.timePeriodList = timePeriodList

        ERROR_MSG("totalAttackTimes  " + str(self.totalAttackTimes) +"  timePeriodList " + timePeriodList.__str__())
        # TODO:调试默认玩家攻击
        self.bAttackList = random.sample(range(1,self.totalAttackTimes), bAttackTimes)
    #  判定进攻发起者Atk1Player
    def __calAtkController(self):
        # 默认是玩家
        self.controllerID = self.avatarAID
        self.defenderID = self.avatarBID
        if self.curAttackIndex in self.bAttackList:
            self.controllerID = self.avatarBID
            self.defenderID = self.avatarAID





    # 计算每个球员的发起进攻值C1
    def __calcObjAttckValue(self,id):
        obj = KBEngine.entities.get(id)
        pos = obj.pos
        posConfig = positionConfig.PositionConfig[pos]
        # 发起进攻值C1 = 球员的控球值 * 球员所处位置的控球系数 + 球员传球值 * 球员所处位置的传球系数
        controll = obj.getControll()
        passBall = obj.getPassBall()
        controll = controll * posConfig["controll"] + passBall * posConfig["pass"]

        # keyStr = "objID - "+str(obj.id)+"   pos :" + str(pos) +"|   obj.controll:" + str(obj.controll)+"|   posConfig['controll']:"+str(posConfig["controll"])
        # keyStr = keyStr + "|   obj.passBall" + str(obj.passBall) + "|    posConfig['pass']" + str(posConfig["pass"])
        # ERROR_MSG(keyStr)
        return controll

    """
    step 4.1 判定进攻发起者Atk1Player
	4.11 判定阵型中的参与进攻球员=a1、a2、a3……an<-可参与进攻球员见属性设定sheet中的【隐性属性】
	4.12 发起进攻值C1=球员的控球值*球员所处位置的控球系数+球员传球值*球员所处位置的传球系数
	4.13 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
	4.14 根据参与进攻的球员随机一个球员判定为【进攻发起者】Atk1Player

    """
    def getAttackerID(self, part):
        controllerObj = KBEngine.entities.get(self.controllerID)

        # 所有已经参与过进攻的参与者
        if hasattr(controllerObj,"preAttackId") is False:
            controllerObj.preAttackId = -1

        sumAttack = 0.0
        stepList = []
        rangeId = []
        canAttackPos = "can   Attack  Pos  "
        for id in controllerObj.inTeamcardIDList:
            if id == controllerObj.preAttackId:
                continue
            obj = KBEngine.entities.get(id)
            if positionConfig.PositionConfig[obj.pos]["attackEnable"] != 1:
                continue

            canAttackPos = canAttackPos+"  "  + str(obj.pos)
            c1 = self.__calcObjAttckValue(id)

            if part == 2:
                c1 = c1 * (1+ obj.secondStepAttackSkillPer)
            elif part == 3:
                c1 = c1 * (1 + obj.thirdStepAttackSkillPer)
            sumAttack = sumAttack + c1

            stepList.append(sumAttack)
            rangeId.append(id)

        # ERROR_MSG(canAttackPos)
        seed = random.uniform(0.0,sumAttack)

        keyStr = "-----------  seed :" + str(seed) + "   "
        for i in range(len(stepList)):
            keyStr = keyStr + "  id :" + str(rangeId[i-1]) + " step: " + str(stepList[i])

        # ERROR_MSG(keyStr)
        for i in range(len(stepList)):
            if seed <= stepList[i]:
                # 取前一个，第0个的时候就是0
                if i >= 0:
                    i = i-1
                controllerObj.atkList.append(rangeId[i])

                controllerObj.preAttackId = rangeId[i]

                ERROR_MSG(" select atkId =====" + str( rangeId[i]) +"  pos" + str(KBEngine.entities.get(rangeId[i]).pos))
                break




    """
    step 4.2 判定进攻发起者的防守者Def1Player1、Def1Player2
	4.21 判定当前轮次的防守人数： 根据(H-1)随机在区间(0,1]，若随机区间在(0，H-1]则为防守人数S为2，若随机区间>H-1,则防守人数S为1 <-H为step3中计算的防守强度系数
	4.22 判定当前阵型中可参与防守Atk1Player的球员=d1、d2、d3……dn   <-可参与防守球员见攻防对位sheet中的【防守对应逻辑】
	4.23 若可参与防守球员数量>S，则从可参与防守球员中随机S人判定为该轮防守者Def1Player1、Def1Player2
	4.24 若可参与防守球员数量<=S，则所有可参与防守的球员都判定为该轮防守者Def1Player1、Def1Player2
	4.25 若没有可参与防守的球员，则该轮无防守球员
    """
    def __getDefPlayerID(self,part):

        if self.controllerID == self.avatarAID:
            ERROR_MSG("current atk controller is A         ")
        else:
            ERROR_MSG("current atk controller is B         ")

        defObj = KBEngine.entities.get(self.defenderID)
        controllerObj = KBEngine.entities.get(self.controllerID)

        aH = defObj.totalDefendValue/controllerObj.totalAttackValue

        # 所有已经参与过进攻的参与者
        if hasattr(defObj,"preDefIds") is False:
            defObj.preDefIds = []

        seed = util.randFunc()

        defCount = 1
        if seed  <= aH -1:
            defCount = 2


        curAttackCardObj = KBEngine.entities.get(self.getCurRoundAtkId(part))

        pos = curAttackCardObj.pos

        posConfig = positionConfig.PositionConfig[pos]

        if "adaptDef" not in posConfig.keys():
            return []


        adaptDefList = posConfig["adaptDef"]

        # skkk = "__getDefPlayerID  atk pos ------------" + str(pos) + " adaptDefList "
        # for l in adaptDefList:
        #     skkk = skkk + "  "+ str(l)
        #
        # ERROR_MSG(skkk)

        sss = "__getDefPlayerID rest card pos"

        canDefList =[]
        for id in defObj.inTeamcardIDList:
            if id in defObj.preDefIds:
                continue

            card = KBEngine.entities.get(id)
            sss = sss + "  " + str(card.pos)
            if card.pos in adaptDefList:
                canDefList.append(id)


        # ERROR_MSG(sss)

        # skkk = "canDefList ------------"
        # for l in canDefList:
        #     skkk = skkk + "  " + str(l) + "  "+ str(KBEngine.entities[l].pos)
        #
        # ERROR_MSG(skkk)

        defCount = min(defCount, len(canDefList))

        defIdList = random.sample(canDefList,defCount)

        defObj.defList.append(defIdList)

        defObj.preDefIds.extend(defIdList)




    """
    step 4.8 第一轮PK为传球轮：判定【进攻发起者Atk1Player VS 进攻发起者的防守者Def1Player】回合结果，若进攻成功进入下一流程step 4.9，若失败跳出这一回合，进入step5
	4.81 若该轮有1个防守者时，判断是否被抢断，若被抢断则进攻结束，直接跳出Step4
		P1=(防守者1抢断值-进攻者盘带值*0.8)*(1-进攻者技术值+防守者身体值)/进攻者等级抢断系数   <-等级抢断系数待定
		根据P1在区间(0,1 ]， 随机结果判断是否被抢断
	4.82 若该轮有2个防守者时，判断是否被第2个防守者抢断，若被抢断则进攻结束，直接跳出Step4；若无第2个防守者则进入4.83
		P2=(防守者2抢断值-进攻者盘带值*0.8)*(1-进攻者技术值+防守者身体值)/进攻者等级抢断系数
		根据P2在区间(0,1 ]， 随机结果判断是否被抢断


    """
    def __canSteal(self):
        avatar = KBEngine.entities.get(self.controllerID)
        if hasattr(self,"gmNoSteal") and self.gmNoSteal:
            return  -1
        attackID = self.getCurRoundAtkId(self.curPart)

        attackObj = KBEngine.entities.get(attackID)

        if attackObj is None:
            ERROR_MSG(" ====================================== attackID   is None")
        defList = self.getCurRoundDefList(self.curPart)

        # 突破时
        self.breakTimePassive(attackID,defList)


        # keyStr = "====================== __canSteal  curPart |  " + str(self.curPart)
        # keyStr = keyStr + "| attackObj.reel | " + str(attackObj.reel)
        # keyStr = keyStr +" | attackObj.tech |  " + str(attackObj.tech)
        # keyStr = keyStr + " |attackObj.levelSteal|  " + str(attackObj.levelSteal)
        #
        # DEBUG_MSG( keyStr)


        result = -1
        attackReel = attackObj.getReel() * 0.8

        defCount = len(defList)
        if defCount == 2  and attackObj.skill2_B == 2001:
            attackObj.usePassiveSkill200101()
        for id in defList:
            defPlayer = KBEngine.entities.get(id)
            # (防守者1抢断值-进攻者盘带值*0.8)*(1-进攻者技术值+防守者身体值)/进攻者等级抢断系数
            steal = defPlayer.getSteal()
            p = (steal - attackReel) * (1 - attackObj.tech + defPlayer.health)/ attackObj.levelSteal

            p = p - attackObj.breakthroughSkillPer

            seed = util.randFunc()
            ERROR_MSG("L385   " + "steal | " + str(steal) + "  | attackReel=" + str(attackReel) + " | attackObj.tech = " + str(attackObj.tech) +" |defPlayer.health= " + str(defPlayer.health) +" |attackObj.levelSteal=" + str(attackObj.levelSteal))


            if  seed <= p:
                result = id
                self.usePassiveSkill(attackID,PassiveSkillCondition.be_steal)

                break

            if defCount == 2:
                attackObj.usePassiveSkill200102()

        # # TODO:调试用。，必然守门员抢断
        # if self.curPart == 3:
        #     defendObj = KBEngine.entities.get(self.defenderID)
        #     result = defendObj.keeperID

        return  result

    """
    4.83 计算传球后的结果O1
		P3=(进攻者传球值-防守者拦截值*0.8)*(1+进攻者技术值-防守者身体值)/进攻者等级传球系数  <-等级传球系数待定
		防守者拦截值=(防守者1拦截值+防守者2拦截值)*防守人数拦截系数 <-防守人数拦截系数：1人防守时为 1   ，2人防守时为 0.75
		防守者身体值=(防守者1身体值+防守者2身体值)*防守人数身体系数<-防守人数身体系数：1人防守时为 1   ，2人防守时为 0.75
		根据P3在区间(0,1]，随机结果判断是否传出【完美助攻】，若结果为完美助攻，下一个接球者传球、射门值均提高20%，O1=1.2；否则O1=1
    """
    def __isPerfectPassBall(self):

        controllerObj = KBEngine.entities.get(self.controllerID)

        attackObj = KBEngine.entities.get(self.getCurRoundAtkId(self.curPart))

        defList = self.getCurRoundDefList(self.curPart)


        self.passTimePassive(attackObj.id)

        defCount = len(defList)
        # 防守者拦截值 防守者身体值
        defTrickSum = 0.0
        defHealthSum = 0.0

        # 防守人数拦截系数
        trickRatio = 1
        healthRatio = 1
        if defCount == 2:
            trickRatio = 0.75
            healthRatio =0.75

        for id in defList:
            defPlayer = KBEngine.entities.get(id)

            defTrickSum  = defTrickSum + defPlayer.getTrick() * trickRatio
            defHealthSum = defHealthSum + defPlayer.health * healthRatio

        # P3 =(进攻者传球值 - 防守者拦截值 * 0.8) * (1 + 进攻者技术值 - 防守者身体值) / 进攻者等级传球系数 < -等级传球系数待定
        passBall = attackObj.getPassBall()

        ERROR_MSG(" L 441   passBall = " + str(passBall) +  " | defTrickSum= " + str(defTrickSum) + " | attackObj.tech = " +str(attackObj.tech) +  " | defHealthSum= " + str(defHealthSum) +str(attackObj.tech) +  " | attackObj.levelPass= " + str(attackObj.levelPass))

        p = (passBall - defTrickSum * 0.8) * (1 + attackObj.tech - defHealthSum) / attackObj.levelPass

        ERROR_MSG(
            "  L445   p  " + str(p) + "  attackObj.perfectPassballSkillPer   " + str(attackObj.perfectPassballSkillPer))
        p = p + attackObj.perfectPassballSkillPer
        seed = util.randFunc()


        controllerObj.o1 = 1.0

        result = False
        if  seed<= p:
            controllerObj.o1 = 1.2
            result = True
        return  result


    """
    4.93 计算射门结果
	P3=(进攻者射门值*O1*L1-防守者防守值)*(1+进攻者技术值-防守者身体值)*(0.95*rand()+0.1)/门将守门值  <O1为4.83中计算的完美助攻系数；L1为射门位置的射门威力系数，系数见【射门位置及系数sheet】
	防守者防守值=(防守者1防守值+防守者2防守值+门将防守值)*防守人数防守系数  <-防守人数防守系数：1人防守时为 1   ，2人防守时为 0.75  ，3人防守时为 0.6 (人数为算上门将的人数)
	防守者身体值=(防守者1身体值+防守者2身体值+门将身体值)*防守人数防守系数  <-防守人数防守系数：1人防守时为 1   ，2人防守时为 0.75  ，3人防守时为 0.6 (人数为算上门将的人数)
	根据P3在区间(0,1]，随机结果判断是否进球

    """
    def getShootValue(self):

        defenderObj = KBEngine.entities.get(self.defenderID)

        if self.reShootCardID != -1:
            attackObj = KBEngine.entities.get(self.reShootCardID)
        else:

            attackID = self.getCurRoundAtkId(self.curPart)
            ERROR_MSG(" getShootValue error  attackID  ==============  " + str(attackID))
            attackObj = KBEngine.entities.get(attackID)


        if attackObj is None:
            ERROR_MSG("========getShootValue  ==== attackObj is None======================")

        # 门将
        keeperObj = KBEngine.entities.get(defenderObj.keeperID)
        if self.reShootCardID != -1:
            defList = []
        else:
            defList = self.getCurRoundDefList(self.curPart)

        self.defendShootTimePassive(defList,defenderObj.keeperID)

        defCount = len(defList) + 1  # +1 为门将

        # 防守人数拦截系数
        defRatio = 1
        if defCount == 2:
            defRatio = 0.75
        elif defCount == 3:
            defRatio = 0.6

        # 防守者防守值 防守者身体值
        defSum = keeperObj.getDefend() * defRatio
        defHealth = keeperObj.health * defRatio
        # 防守者防守值=(防守者1防守值+防守者2防守值+门将防守值)*防守人数防守系数
        for id in defList:
            defPlayer = KBEngine.entities.get(id)

            defSum = defSum + defPlayer.getDefend() * defRatio
            defHealth = defHealth + defPlayer.health * defRatio

            #     P3=(进攻者射门值*O1*L1-防守者防守值)*(1+进攻者技术值-防守者身体值)*(0.1*rand()+0.95)/门将守门值

        controllerObj = KBEngine.entities.get(self.controllerID)
        posStr = ""
        for pos in controllerObj.atkPosList:

            posStr = posStr + "    "+str(pos)
        ERROR_MSG("curPart ----- " + str(self.curPart) +"    posStr==   "+ posStr )


        if self.reShootCardID != -1:
            L1 = 0.6
        else:
            coordinate = self.getCurRoundAtkCoordinate(self.curPart)
            L1 = positionAttribute.PositionAttribute[coordinate]["powerPer"]

        shootValue = attackObj.getShoot()
        keeperKeep = keeperObj.getKeep()
        p = (shootValue * controllerObj.o1 * L1 - defSum) * (1 + attackObj.tech - defHealth) * ( 0.1 * random.random() + 0.95) / keeperKeep
        p = p + attackObj.shootSuccSkillPer

        return p

    def isShootSucc(self):
        # TODO:如果补射不为空 射门失败
        if self.reShootCardID != -1:
            return False
        if self.isShootMiss() is True:
            return False
        p = self.getShootValue()

        seed = util.randFunc()

        shootSucc = False
        if seed <= p:
            shootSucc = True


        return  shootSucc
    # 是否射偏
    def isShootMiss(self):
        attackObj = KBEngine.entities.get(self.getCurRoundAtkId(self.curPart))
        missPercent = attackObj.shootMissSkillPer

        seed = util.randFunc()

        if missPercent >= seed:
            return True
        return False

    """
    step 4.7 判定Atk1Player、Atk2Player、Atk3Player的进攻位置；根据进攻队员位置判定Def1Player1、Def1Player2、Def2Player1、Def2Player2、Def3Player1、Def3Player2的防守位置
	4.71 根据【射门位置及系数sheet】中逻辑，将4.1~4.6所获得的球员随机到相应进攻/防守位置上

	曾经用过的点不再用
    """
    def __getAtkCoordinate(self,part):

        controller = KBEngine.entities.get(self.controllerID)
        attackObj = KBEngine.entities.get(controller.atkList[part - 1])

        pos = attackObj.pos
        curRound = "round" + str(part)
        # 候选的攻击点
        candidateTuple = playerAtkPosition.PlayerAtkPosition[pos][curRound]

        candidateList = [i for i in  candidateTuple if i not in controller.atkPosList]
        # 选中的坐标
        coordinate = random.choice(candidateList)


        # keyStr = "__getAtkCoordinate =======   attackObj  ID    "+str(attackObj.id)+"  part   " + str(self.curPart)
        # keyStr = keyStr +"   coordinate:     "+ str(coordinate) +"         "
        #
        # for po in candidateList:
        #     keyStr = keyStr + "     |      " + str(po)
        #
        # ERROR_MSG(keyStr)

        controller.atkPosList.append(coordinate)

        ERROR_MSG("attackObj id  " + str(attackObj.id) +"   pos  " + str(attackObj.pos) + "   coordinate  " + str(coordinate))


    # 开始战斗
    def onCmdBeginFight(self):
        self.calcBaseData()

        # 通知客户端总的攻击次数
        avatarA = KBEngine.entities.get(self.avatarAID)

        if isinstance(avatarA,Avatar.Avatar):
            avatarA.client.onTotalAttackTimes(self.totalAttackTimes)

        avatarB = KBEngine.entities.get(self.avatarBID)
        if isinstance(avatarB, Avatar.Avatar):
            avatarB.client.onTotalAttackTimes(self.totalAttackTimes)

        self.onCmdNextRound()

    # 客户端动画播放完毕
    def onCmdPlayAnimFinish(self,controllerID):

        if controllerID == self.avatarAID:
            self.aAnimFinish = True
            # 使用前置技能
        if controllerID == self.avatarBID:
            self.bAnimFinish = True
        if self.aAnimFinish and self.bAnimFinish:
            self.aAnimFinish = False
            self.bAnimFinish = False

            if self.endRound is True:
                ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  end round-------------------------------------------------------")

                avatarA = KBEngine.entities.get(self.avatarAID)
                if isinstance(avatarA, Avatar.Avatar):

                    ERROR_MSG("onCmdPlayAnimFinish   ascore  " + str(self.aScore) )
                    avatarA.client.onRoundEnd(self.aScore,self.bScore)

                avatarB = KBEngine.entities.get(self.avatarBID)
                if isinstance(avatarB, Avatar.Avatar):
                    avatarB.client.onRoundEnd(self.bScore,self.aScore)
                # 进入下一轮
                self.onCmdNextRound()
                return
            self.curPart = self.curPart + 1
            if  self.curPart == 2:
                ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  2 part-------------------------------------------------------")
                self.__onSecondPart()
            if self.curPart == 3:
                ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  3 part-------------------------------------------------------")
                self.__onThirdPart()

    # 客户端选择技能
    def onCmdSelectSkill(self, op):
        #
        # ERROR_MSG( "--------------------------------onCmdSelectSkill--- part ---------" + str(self.curPart) +"       skillId   "+ str(skillId))
        # 补射
        if self.reShootCardID != -1:
            self.roundResult = self.onCmdShoot()
            self.reShootCardID = -1
            self.noticeClientResult()
        else:
            if self.curPart == 1:
                if op == PlayerOp.passball:
                    self.roundResult  = self.onCmdPass()
                else:
                    ERROR_MSG("  error  1 " )
                ERROR_MSG( "  error  1 " + str(self.roundResult) )
            elif self.curPart == 2:
                if op == PlayerOp.passball:
                    self.roundResult = self.onCmdPass()
                elif op == PlayerOp.shoot:
                    self.roundResult = self.onCmdShoot()
                ERROR_MSG("  error  2 " + str(self.roundResult))
            elif self.curPart == 3:
                if op == PlayerOp.shoot:
                    self.roundResult = self.onCmdShoot()
                else:
                    ERROR_MSG("  error  3 ")
                ERROR_MSG("  error  3 " + str(self.roundResult))
            avatarA = KBEngine.entities.get(self.avatarAID)
            avatarB = KBEngine.entities.get(self.avatarBID)

            if self.roundResult == ConditionEnum.con_result_be_keeper_steal:
                self.roundResult = ConditionEnum.con_result_be_steal
            if self.roundResult == ConditionEnum.con_result_reshoot_fail:
                self.roundResult = ConditionEnum.con_result_shoot_fail

                ERROR_MSG("  onCmdSelectSkill    reshoot fail")
            if self.roundResult == ConditionEnum.con_result_reshoot_succ:
                self.roundResult = ConditionEnum.con_result_shoot_succ
                ERROR_MSG("  onCmdSelectSkill    reshoot succ")

            avatarA.controllerAfterRound(self.roundResult)
            avatarB.controllerAfterRound(self.roundResult)


            self.noticeClientResult()


    def noticeClientResult(self):
        avatarA = KBEngine.entities.get(self.avatarAID)
        avatarB = KBEngine.entities.get(self.avatarBID)

        if self.roundResult == -1:
            ERROR_MSG(util.printStackTrace("     round result is -1"))


        ERROR_MSG("noticeClientResult    " + str(self.roundResult))

        if isinstance(avatarA, Avatar.Avatar):
            avatarA.client.onOprateResult(self.curPart, self.roundResult)

        if isinstance(avatarB, Avatar.Avatar):
            avatarB.client.onOprateResult(self.curPart, self.roundResult)

    # 下一轮
    def onCmdNextRound(self):

        # 当前进攻序列
        self.curAttackIndex = self.curAttackIndex + 1
        avatarA = KBEngine.entities.get(self.avatarAID)
        avatarB = KBEngine.entities.get(self.avatarBID)
        # 本局结束
        if self.curAttackIndex >= self.totalAttackTimes:
            if self.half == HalfEnum.sencond:
                if isinstance(avatarA,Avatar.Avatar):
                    avatarA.client.onGameOver()
                if isinstance(avatarB, Avatar.Avatar):
                    avatarB.client.onGameOver()
                # 传送出去结果
                if avatarA.typeStr == "Avatar":
                    avatarA.base.onRoomEndResult(self.avatarAID,self.aScore,self.avatarBID,self.bScore)
                if avatarB.typeStr == "Avatar":
                    avatarB.base.onRoomEndResult( self.avatarAID, self.aScore, self.avatarBID, self.bScore)


                return
            else:
                self.addTimer(10,0,TimerDefine.Time_halfTime)
                return


        if isinstance(avatarA, Avatar.Avatar):
            avatarA.client.onCurAttackIndex(self.curAttackIndex)
        if isinstance(avatarB, Avatar.Avatar):
            avatarB.client.onCurAttackIndex(self.curAttackIndex)

        # 当前攻击的是玩家还是副本
        self.__calAtkController()

        curTime = self.timePeriodList[self.curAttackIndex]
        # ①重置临时数据
        avatarA.beforeRound(curTime)
        avatarB.beforeRound(curTime)
        # 当前序列的第几轮
        self.curPart = 1
        #
        self.endRound = False
        self.roundResult = -1
        self.aSelect = False
        self.bSelect = False

        controllerObj = KBEngine.entities.get(self.controllerID)
        defObj = KBEngine.entities.get(self.defenderID)

        controllerObj.atkList = []
        controllerObj.atkPosList = []
        defObj.defList = []
        defObj.preDefIds = []
        for part in range(3):
            self.getAttackerID(part + 1)
            self.__getDefPlayerID(part + 1)

            controllerObj = KBEngine.entities.get(self.controllerID)
            defObj = KBEngine.entities.get(self.defenderID)

            ERROR_MSG( str(part) +" - round  atk    " + str(controllerObj.atkList[part]) )
            ERROR_MSG( str(part) + " - round  defend   " + str(defObj.defList[part]))
            self.__getAtkCoordinate(part + 1)
        ERROR_MSG("onCmdNextRound          select     end")

        atkList = controllerObj.atkList
        atkPosList = controllerObj.atkPosList
        firstDefList = defObj.defList[0]
        secondDefList = defObj.defList[1]
        thirdDefList = defObj.defList[2]

        atkIDStr = "atkID      "
        for id in controllerObj.atkList:
            atkIDStr = atkIDStr + "  id  " + str(id) +" pos " +str(KBEngine.entities[id].pos)

        # ERROR_MSG(atkIDStr)
        #
        # atkIDStr = "atkPosList      "
        # for id in controllerObj.atkPosList:
        #     atkIDStr = atkIDStr + "     coordinate  " + str(id)
        #
        # ERROR_MSG(atkIDStr)
        #
        # firstDefListStr = "firstDefList      "
        # for id in firstDefList:
        #     firstDefListStr = firstDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)
        #
        # ERROR_MSG(firstDefListStr)
        #
        # secondDefListStr = "secondDefList      "
        # for id in secondDefList:
        #     secondDefListStr = secondDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)
        #
        # ERROR_MSG(secondDefListStr)

        # thirdDefListStr = "thirdDefList      "
        # for id in thirdDefList:
        #     thirdDefListStr = thirdDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)
        #
        # ERROR_MSG(thirdDefListStr)

        # ERROR_MSG("-----------------------------defObj.keeperID -------------------  " + str(defObj.keeperID) + "   objID   "+ str(defObj.id))



        if isinstance(avatarA, Avatar.Avatar):
            avatarA.client.onAtkAndDefID(curTime,atkList,atkPosList, firstDefList,secondDefList,thirdDefList,defObj.keeperID)
        if isinstance(avatarB, Avatar.Avatar):
            avatarB.client.onAtkAndDefID(curTime,atkList,atkPosList, firstDefList,secondDefList,thirdDefList,defObj.keeperID)

        thirdDefList.append(defObj.keeperID)
        # 第一步
        self.__onFirstPart()



    # 第一步
    def __onFirstPart(self,skillId = -1):
        # 副本直接选择传球
        controller = KBEngine.entities.get(self.controllerID)
        defender =  KBEngine.entities.get(self.defenderID)
        self.addAnger(self.curPart)

        canUseSkillList = controller.selectCanUseSkills()
        # 不是avatar 就调用AI
        if isinstance(controller, Avatar.Avatar):
            controller.client.onSelectSkill(self.curPart, canUseSkillList)

            ERROR_MSG(" __onFirstPart  c  " + canUseSkillList.__str__())
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            controller.onAISelect()
        canUseSkillList = defender.selectCanUseSkills()
        if isinstance(defender, Avatar.Avatar):
            defender.client.onSelectSkill(self.curPart, canUseSkillList)
            ERROR_MSG(" __onFirstPart  d  " + canUseSkillList.__str__())
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            defender.onAISelect()





    def __onSecondPart(self):
        controller = KBEngine.entities.get(self.controllerID)
        defender = KBEngine.entities.get(self.defenderID)
        self.addAnger(self.curPart)
        # 不是avatar 就调用AI
        canUseSkillList = controller.selectCanUseSkills()
        if isinstance(controller, Avatar.Avatar):
            controller.client.onSelectSkill(self.curPart, canUseSkillList)
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            controller.onAISelect()
        canUseSkillList = defender.selectCanUseSkills()
        if isinstance(defender, Avatar.Avatar):
            defender.client.onSelectSkill(self.curPart, canUseSkillList)
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            defender.onAISelect()

    # 第三步
    def __onThirdPart(self):

        controller = KBEngine.entities.get(self.controllerID)
        defender = KBEngine.entities.get(self.defenderID)
        self.addAnger(self.curPart)

        canUseSkillList = controller.selectCanUseSkills()
        # 不是avatar 就调用AI
        if isinstance(controller, Avatar.Avatar):
            controller.client.onSelectSkill(self.curPart, canUseSkillList)
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            controller.onAISelect()
        canUseSkillList = defender.selectCanUseSkills()
        if isinstance(defender, Avatar.Avatar):
            defender.client.onSelectSkill(self.curPart, canUseSkillList)
        else:
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            defender.onAISelect()


    def addAnger(self,part):

        attackID = self.getCurRoundAtkId(self.curPart)
        card = KBEngine.entities.get(attackID)
        card.anger = card.anger + 15

        defList = self.getCurRoundDefList(self.curPart)
        for defID in defList:
            card = KBEngine.entities.get(defID)
            card.anger = card.anger + 10

    def onCmdShoot(self):



        if self.reShootCardID != -1:
            # 补射的时候设置为不可抢断
            stealCardID = -1
        else:
            stealCardID = self.__canSteal()
        ERROR_MSG("onCmdShoot   stealCardID    "+ str(stealCardID) + "  reShootCardID  " + str(self.reShootCardID))

        self.endRound = True



        if stealCardID != -1:
            # 抢断成功 通知客户端播放动画
            ERROR_MSG("-------onOprateResult------trickSucc----------------self.curPart  " + str(self.curPart))
            defendObj = KBEngine.entities.get(self.defenderID)
            if stealCardID == defendObj.keeperID:

                result = ConditionEnum.con_result_be_keeper_steal
            else:
                result = ConditionEnum.con_result_be_steal
        else:
            self.shootTimePassive(self.getCurRoundAtkId(self.curPart))
            shootResult = self.isShootSucc()
            ERROR_MSG("-----------onCmdShoot    " + shootResult.__str__())
            if hasattr(self,"gmShootFail") and self.gmShootFail:
                shootResult =   False
            if hasattr(self, "gmShootSucc") and self.gmShootSucc:
                shootResult = True

            if shootResult:
                # 通知客户端射门成功
                ERROR_MSG("-------onOprateResult------shootSucc 1 ----------------self.curPart  " + str(self.curPart))
                result = ConditionEnum.con_result_shoot_succ

                if self.controllerID == self.avatarAID:
                    self.aScore = self.aScore + 1
                else:
                    self.bScore = self.bScore + 1

                if self.reShootCardID != -1:
                    result  = ConditionEnum.con_result_reshoot_succ
            else:
                # 通知客户端射门失败
                ERROR_MSG("-------onOprateResult------shootFail----------------self.curPart  " + str(self.curPart))
                result = ConditionEnum.con_result_shoot_fail
                if self.reShootCardID != -1:
                    ERROR_MSG("-------onOprateResult------reshoot  Fail----------------self.curPart  " + str(self.curPart))
                    result = ConditionEnum.con_result_reshoot_fail


        return  result

    # 传球
    def onCmdPass(self):
        result = self.__canSteal()
        if result != -1:
            # 抢断成功 通知客户端播放动画
            ERROR_MSG("-------onOprateResult------trickSucc----------------self.curPart  " + str(self.curPart))
            self.endRound = True
            result = ConditionEnum.con_result_be_steal
        else:
            result = self.__isPerfectPassBall()
            if result is True:
                # 通知客户端完美传球
                ERROR_MSG("-------onOprateResult------perfectPassBall----------------self.curPart  " + str(self.curPart))
                result =  ConditionEnum.con_result_perfect_pass
            else:

                ERROR_MSG(util.printStackTrace("passBall"))
                # 通知客户端普通传球
                ERROR_MSG("-------onOprateResult------passBall----------------self.curPart  " + str(self.curPart))
                # self.__onThirdPart()
                result =  ConditionEnum.con_result_pass_succ

        return result


    # 获得当前轮的攻击者ID
    def getCurRoundAtkId(self, part):

        if self.reShootCardID != -1:
            return self.reShootCardID

        controllerObj = KBEngine.entities.get(self.controllerID)


        attackId = -1
        try:
            attackId = controllerObj.atkList[part -1]

            # ERROR_MSG("------------------------self.curPart - 1    "+str(part-1 )+"   attackID-------------" +str(attackId))
        except:
            ERROR_MSG("========= list index out of range  self.curPart  =========  " + str(part-1) +"   atklist len   " + str(len(controllerObj.atkList)))

        return attackId
    # 获得当前轮的攻击者ID的球场坐标
    def getCurRoundAtkCoordinate(self, part):

        controllerObj = KBEngine.entities.get(self.controllerID)


        attackCoordinate = -1
        try:
            attackCoordinate = controllerObj.atkPosList[part -1]

             # ERROR_MSG("------------------------self.curPart - 1    "+str(part-1 )+"   attackCoordinate-------------" +str(attackCoordinate))
        except:
            ERROR_MSG("========= list index out of range  self.curPart  =========  " + str(part-1) +"   atklist len   " + str(len(controllerObj.atkList)))

        return attackCoordinate

    # 获得当前轮的防守者ID List
    def getCurRoundDefList(self, part):

        defObj  = KBEngine.entities.get(self.defenderID)

        defList = defObj.defList[part - 1]

        return defList


    def setControllerID(self,controllerID):

        ERROR_MSG("setControllerID   " + str(controllerID))

        if self.avatarAID == -1:
            self.avatarAID = controllerID
        else:
            self.avatarBID = controllerID

    def setReadyState(self,controllerID):
        ERROR_MSG("setReadyState   " + str(controllerID) + "  aReady  is " + str(self.aReady) +"     bready is " + str(self.bReady))
        if controllerID == self.avatarAID:
            self.aReady = True
        if controllerID == self.avatarBID:
            self.bReady = True

        WARNING_MSG("aReady  is " + str(self.aReady) +"     bready is " + str(self.bReady))
        if self.aReady and self.bReady:

            ERROR_MSG("setReadyState    " + util.printStackTrace("setReadyState"))

            inTeamCardIDList = KBEngine.entities.get(self.avatarAID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                self.usePassiveSkill(cardID, PassiveSkillCondition.game_start)
                self.usePassiveSkill(cardID, PassiveSkillCondition.first_half)

            inTeamCardIDList = KBEngine.entities.get(self.avatarBID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                self.usePassiveSkill(cardID, PassiveSkillCondition.game_start)
                self.usePassiveSkill(cardID, PassiveSkillCondition.first_half)

            self.onCmdBeginFight()


    def setSelectState(self,controllerID,op):
        if op != -1:

            ERROR_MSG(util.printStackTrace( "op select from  "))
            self.curPartOp = op
        if controllerID == self.avatarAID:
            self.aSelect = True
            # 使用前置技能
        if controllerID == self.avatarBID:
            self.bSelect = True
        if self.aSelect and self.bSelect:
            self.aSelect = False
            self.bSelect = False
            self.onCmdSelectSkill(self.curPartOp)


    def onDestroy(self):
        """
        KBEngine method.
        """
        self.destroySpace()

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



    def onTimer(self, id, userArg):
        # ERROR_MSG("ontimer" + str(userArg))
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        if userArg == TimerDefine.Time_halfTime:
            ERROR_MSG(" second  half =======================================================================================================================  ")
            self.delTimer(id)
            self.half = HalfEnum.sencond
            inTeamCardIDList = KBEngine.entities.get(self.avatarAID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                self.usePassiveSkill(cardID, PassiveSkillCondition.second_half)

            inTeamCardIDList = KBEngine.entities.get(self.avatarBID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                self.usePassiveSkill(cardID, PassiveSkillCondition.second_half)
            self.curAttackIndex = 0
            self.onCmdBeginFight()
            pass
        pass

    # 单个卡牌使用被动技能
    def usePassiveSkill(self,cardID,time):
        card = KBEngine.entities.get(cardID)
        card.usePassive(time)



    # 射门的时候（被动技能触发）
    def shootTimePassive(self,cardID):
        pos = self.getCurRoundAtkCoordinate(self.curPart)

        ERROR_MSG("shootTimePassive  shoot pos    "  + str(pos))
        # 小角度射门
        if pos in (12,13,22,23,17,18,27,28):
            self.usePassiveSkill(cardID, PassiveSkillCondition.small_degree_shoot)
        # 禁区内射门
        if pos in (34, 35, 36, 44, 45, 46, 54, 55, 56):
            self.usePassiveSkill(cardID,PassiveSkillCondition.in_penalty_area)
        #  禁区外射门
        if pos not  in (34, 35, 36, 44, 45, 46, 54, 55, 56):
            self.usePassiveSkill(cardID,PassiveSkillCondition.out_penalty_area)


    # 射门的时候-防守方
    def defendShootTimePassive(self,defendList,keepID):
        # 2015 门线救险：门将出击时，奔向门前封堵射门，40%几率封堵穿透门将的射门。
        self.usePassiveSkill(keepID,PassiveSkillCondition.shoot)

        for cardID in defendList:
            self.usePassiveSkill(cardID,PassiveSkillCondition.in_defend)
            # 门墙：身高臂长的库尔图瓦，使得对方前锋射门时必须寻找更刁钻的角度，降低射门者射偏率n%
            self.usePassiveSkill(cardID,PassiveSkillCondition.shoot)

        # 单刀
        # defendList = []
        # ERROR_MSG("2020=================defendList==========================")
        if self.curPart == 3 and len(defendList) == 0:
            inTeamCardIDList = KBEngine.entities.get(self.defenderID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                self.usePassiveSkill(cardID, PassiveSkillCondition.no_defender)
# 传球的时候
    def passTimePassive(self,cardID):
        pos = self.getCurRoundAtkCoordinate(self.curPart)
        if pos in (11,12,21,22,31,32,41,42,18,19,28,29,38,39,48,49):
            # 在边路时
            self.usePassiveSkill(cardID, PassiveSkillCondition.in_wing)
            # 边路传中
            self.usePassiveSkill(cardID, PassiveSkillCondition.pass_in_wings)

        # 下底传中：下底传中时，提升n%传球值
        if pos in (11,12,13,21,22,23,17,18,19,27,28,29):
            self.usePassiveSkill(cardID, PassiveSkillCondition.pass_in_wings)


    # 突破的时候 （攻击方）
    def breakTimePassive(self,attackID,defList):
        self.usePassiveSkill(attackID, PassiveSkillCondition.break_start)
        self.usePassiveSkill(attackID, PassiveSkillCondition.attacker)
        for cardID in defList:
            self.usePassiveSkill(cardID, PassiveSkillCondition.in_defend)
        # 2013 佯装接应：本方球员（除自己）面对两人防守时，有几率插上带走一个防守球员
        if len(defList) == 2:
            ERROR_MSG("breakTimePassive           ++++++++++++++++++++++++++++++++++++++++++++             ")
            inTeamCardIDList = KBEngine.entities.get(self.controllerID).inTeamcardIDList
            for cardID in inTeamCardIDList:
                if attackID != cardID:
                    self.usePassiveSkill(cardID, PassiveSkillCondition.two_defender)



    # 被抢断的时候
    def beStealTimePassive(self,cardID):
        self.usePassiveSkill(cardID, PassiveSkillCondition.be_steal)




    #=========================================================================
    def destroyRoom(self):
        ERROR_MSG(" destroyRoom is called ")
        self.destroy()

class ClientResult:
    # 抢断成功
    trickSucc = 1
    # 普通传球
    passBall = 2
    # 完美传球
    perfectPassBall = 3
    # 射门成功
    shootSucc = 4
    # 射门失败
    shootFail = 5
    # 选择射门还是传球
    select = 6


if __name__ == '__main__':
    pass