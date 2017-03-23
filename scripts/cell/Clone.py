# -*- coding: utf-8 -*-
import KBEngine
import random

import TimerDefine
import cloneConfig
import monsterConfig
import formationConfig
import playerAtkPosition
import positionAttribute
import positionConfig
import util
from KBEDebug import *

class Clone(KBEngine.Entity):

#========================KBE方法=================================================
    """
    游戏房间
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        print("Cell::clone.__init__")
        KBEngine.globalData["room_%i" % self.spaceID] = self.base



        # 注册clone管理的属性
        self.initProp()
        # 初始化怪
        self.initMonster()

    # 初始化 副本管理的属性
    def initProp(self):
        """
        clone管理的副本全局数据
        """
        self.avatarID = -1
        # 总的回合次数
        self.totalAttackTimes = 0
        # 当前进攻序列
        self.curAttackIndex = -1
        # 当前控制者(玩家或者副本)
        self.controllerID = 0
        # 当前防守者的控制者
        self.defenderID = 0
        # 当前回合的第几轮
        self.curPart = 1
        # 是否结束此轮
        self.endRound = False
        # 怪的攻击序列
        self.monsterAttackList = []


        # --------------------------------------------------------------------------------------------------------------
        """
        clone 管理的 怪的数据
        """
        self.totalAttackValue = 0.0
        self.totalDefendValue =0.0
        self.totalControllValue = 0.0
        # 当前怪的id list
        self.inTeamcardIDList = []
        # 上一轮的攻击者
        self.preAttackId = -1
        # 上一轮的防守者 列表
        self.preDefIds = []
        # 上一轮是否完美助攻的射门系数
        self.o1 = 1

        self.atkList = []
        self.atkPosList = []
        self.defList = []

        # 门将id
        self.keeperID = -1

        # 技术统计 TODO:
        # 被抢断
        self.beTrick = 0
        # 防守成功次数
        self.defSucc = 0
        # 射门成功
        self.shootSucc = 0


        pass

    """
    初始化怪
    """
    def initMonster(self):

        cloneNpcConfig = cloneConfig.CloneConfig[self.cloneID]

        npcTuple = cloneNpcConfig["npcTuple"]

        formationTuple = cloneNpcConfig["formationTuple"]

        errorMsg = "========monster pos ========="

        for i in range(11):
            npcID = npcTuple[i]
            if npcID not in monsterConfig.MonsterConfig:
                ERROR_MSG("wrong config")
                continue
            baseProp = monsterConfig.MonsterConfig[npcID]

            param = {"monsterID"    : npcID,
                     "shoot"        : baseProp["shoot"],
                     "defend"       : baseProp["defend"],
                     "passBall"     : baseProp["pass"],
                     "trick"         : baseProp["trick"],
                     "reel"          : baseProp["reel"],
                     "steal"         : baseProp["steal"],
                     "controll"      : baseProp["controll"],
                     "keep"          : baseProp["keep"],
                     "tech"          : baseProp["tech"],
                     "health"        : baseProp["health"],
                     "pos"            : formationTuple[i],
                     "levelSteal"    :baseProp["levelStealRatio"],
                     "levelPass"     :baseProp["levelPassRatio"]
                    }


            position = (0.0,0.0,0.0)
            direction = (0.0,0.0,0.0)
            e = KBEngine.createEntity("Monster",self.spaceID,position,direction,param)
            # 门将

            errorMsg = errorMsg + "      " + str(e.pos)
            if e.pos == 1:
                self.keeperID = e.id
                # ERROR_MSG("-------------------monster-----------keeperID------------------------------  " + str(e.id))
            self.inTeamcardIDList.append(e.id)

        ERROR_MSG(errorMsg)


    # 计算进攻次数
    def __calcAttackTimes(self, aID, bID):

        # A队进攻次数MA=max(round(回合设定基数*(A队攻击系数+B队攻击系数-5)/(A队防御系数+B队防御系数-5)*(A队控球系数)/(A队控球系数+B队控球系数)*(0.1*rand(1)+0.95),0),1)
        roundBase = 6
        seed = random.random()

        a = KBEngine.entities.get(aID)
        b = KBEngine.entities.get(bID)

        attackTimes = max(round(roundBase * (a.totalAttackValue + b.totalAttackValue - 5) / (a.totalDefendValue + b.totalDefendValue - 5) * (a.totalControllValue) / (a.totalControllValue + b.totalControllValue) * (0.1 * seed + 0.95), 0), 1)

        return  int(attackTimes)

    # 计算玩家总的攻击系数 和 防守次数 和控球系数
    def __calMyAtkAndDefendAndControllValue(self):
        avartar = KBEngine.entities.get(self.avatarID)
        if avartar is None:
            return 0,0,0
        myFormation = avartar.formation

        attack = 0.0
        defend = 0.0
        controll = 0.0

        posList = formationConfig.FormationConfig[myFormation]["teamTuple"]

        for pos in posList:

            posConfig = positionConfig.PositionConfig[pos]

            if posConfig["attackEnable"] == 1:
                attack = attack + posConfig["attack"]
            defend = defend + posConfig["defend"]
            controll = controll + posConfig["controll"]

        return  attack,defend,controll

    # 计算怪的总的攻击系数 和 防守次数 和控球系数
    def __calMonsterAtkAndDefendAndControllValue(self):
        attack = 0.0
        defend = 0.0
        controll = 0.0
        for id in self.inTeamcardIDList:
            monster = KBEngine.entities.get(id)
            pos = monster.pos
            posConfig = positionConfig.PositionConfig[pos]
            if posConfig["attackEnable"] == 1:
                attack = attack + posConfig["attack"]
            defend = defend + posConfig["defend"]
            controll = controll + posConfig["controll"]

        return attack,defend,controll


    """
       计算基础的数据
   """
    def calcBaseData(self):
        avatar = KBEngine.entities.get(self.avatarID)

        # 玩家总的攻击系数 和 防御系数  和 控球系数
        avatar.totalAttackValue, avatar.totalDefendValue, avatar.totalControllValue = self.__calMyAtkAndDefendAndControllValue()

        # 怪总的攻击系数 和 防御系数 和 控球系数
        self.totalAttackValue, self.totalDefendValue, self.totalControllValue = self.__calMonsterAtkAndDefendAndControllValue()

        myattackTimes = self.__calcAttackTimes(self.avatarID, self.id)
        monsterAttackTimes = self.__calcAttackTimes(self.id, self.avatarID)

        self.totalAttackTimes = myattackTimes + monsterAttackTimes

        self.monsterAttackList = random.sample(range(self.totalAttackTimes), monsterAttackTimes)
    #  判定进攻发起者Atk1Player
    def __calAtkController(self):
        # 默认是玩家
        self.controllerID = self.avatarID
        self.defenderID = self.id
        if self.curAttackIndex in self.monsterAttackList:
            self.controllerID = self.id
            self.defenderID = self.avatarID



    # 计算每个球员的发起进攻值C1
    def __calcObjAttckValue(self,obj):

        pos = obj.pos
        posConfig = positionConfig.PositionConfig[pos]
        # 发起进攻值C1 = 球员的控球值 * 球员所处位置的控球系数 + 球员传球值 * 球员所处位置的传球系数
        controll = obj.controll * posConfig["controll"] + obj.passBall * posConfig["pass"]

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
    def __GetAttackerID(self,part):
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
            c1 = self.__calcObjAttckValue(obj)
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

        if self.controllerID == self.id:
            ERROR_MSG("current atk controller is clone         ")
        else:
            ERROR_MSG("current atk controller is avatar         ")

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


        curAttackCardObj = KBEngine.entities.get(self.__getCurRoundAtkId(part))

        pos = curAttackCardObj.pos

        posConfig = positionConfig.PositionConfig[pos]

        if "adaptDef" not in posConfig.keys():
            return []


        adaptDefList = posConfig["adaptDef"]

        skkk = "atk pos ------------" + str(pos) + " adaptDefList "
        for l in adaptDefList:
            skkk = skkk + "  "+ str(l)

        ERROR_MSG(skkk)

        sss = " rest card pos"

        canDefList =[]
        for id in defObj.inTeamcardIDList:
            if id in defObj.preDefIds:
                continue

            card = KBEngine.entities.get(id)
            sss = sss + "  " + str(card.pos)
            if card.pos in adaptDefList:
              canDefList.append(id)


        ERROR_MSG(sss)

        skkk = "canDefList ------------"
        for l in canDefList:
            skkk = skkk + "  " + str(l) + "  "+ str(KBEngine.entities[l].pos)

        ERROR_MSG(skkk)

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

        attackID = self.__getCurRoundAtkId(self.curPart)

        attackObj = KBEngine.entities.get(attackID)

        if attackObj is None:
            ERROR_MSG(" ====================================== attackID   is None")
        defList = self.__getCurRoundDefList(self.curPart)

        # keyStr = "====================== __canSteal  curPart |  " + str(self.curPart)
        # keyStr = keyStr + "| attackObj.reel | " + str(attackObj.reel)
        # keyStr = keyStr +" | attackObj.tech |  " + str(attackObj.tech)
        # keyStr = keyStr + " |attackObj.levelSteal|  " + str(attackObj.levelSteal)
        #
        # DEBUG_MSG( keyStr)


        result = False
        for id in defList:
            defPlayer = KBEngine.entities.get(id)
            # P1 =(防守者1抢断值 - 进攻者盘带值) * (1 - 进攻者技术值 + 防守者身体值) / 进攻者等级抢断系数

            p = (defPlayer.steal - attackObj.reel * 0.8) * (1 - attackObj.tech + defPlayer.health)/ attackObj.levelSteal

            seed = util.randFunc()

            # DEBUG_MSG("__canSteal  curPart |  " + str(self.curPart) + "| defPlayer | " + str(defPlayer.steal) + "  | defPlayer.health |  " + str(defPlayer.health) + " | p     |  " + str(p) + "  |     seed|  " + str(seed))
            if  seed <= p:
                result = True
                break

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

        attackObj = KBEngine.entities.get(self.__getCurRoundAtkId(self.curPart))

        defList = self.__getCurRoundDefList(self.curPart)

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

            defTrickSum  = defTrickSum + defPlayer.trick * trickRatio
            defHealthSum = defHealthSum + defPlayer.health * healthRatio

        # P3 =(进攻者传球值 - 防守者拦截值 * 0.8) * (1 + 进攻者技术值 - 防守者身体值) / 进攻者等级传球系数 < -等级传球系数待定
        p = (attackObj.passBall - defTrickSum * 0.8) * (1 + attackObj.tech - defHealthSum) / attackObj.levelPass

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
    def __getShootValue(self):

        controllerObj = KBEngine.entities.get(self.controllerID)


        attackObj = KBEngine.entities.get(self.__getCurRoundAtkId(self.curPart))
        # 门将
        keeperObj = KBEngine.entities.get(controllerObj.keeperID)

        defList = self.__getCurRoundDefList(self.curPart)

        defCount = len(defList) + 1  # +1 为门将

        # 防守人数拦截系数
        defRatio = 1
        if defCount == 2:
            defRatio = 0.75
        elif defCount == 3:
            defRatio = 0.6

        # 防守者防守值 防守者身体值
        defSum = keeperObj.defend * defRatio
        defHealth = keeperObj.health * defRatio
        # 防守者防守值=(防守者1防守值+防守者2防守值+门将防守值)*防守人数防守系数
        # 防守者身体值=(防守者1身体值+防守者2身体值+门将身体值)*防守人数防守系数
        for id in defList:
            defPlayer = KBEngine.entities.get(id)

            defSum = defSum + defPlayer.defend * defRatio
            defHealth = defHealth + defPlayer.health * defRatio

            #     P3=(进攻者射门值*O1*L1-防守者防守值)*(1+进攻者技术值-防守者身体值)*(0.1*rand()+0.95)/门将守门值

        posStr = ""
        for pos in controllerObj.atkPosList:

            posStr = posStr + "    "+str(pos)
        ERROR_MSG("curPart ----- " + str(self.curPart) +"    posStr==   "+ posStr )
        coordinate =  self.__getCurRoundAtkCoordinate(self.curPart)

        L1 = positionAttribute.PositionAttribute[coordinate]["powerPer"]

        p = (attackObj.shoot * controllerObj.o1 * L1 - defSum) * (1 + attackObj.tech - defHealth) * ( 0.1 * random.random() + 0.95) / keeperObj.keep

        return p

    def __isShootSucc(self):

        p = self.__getShootValue()

        seed = util.randFunc()

        shootSucc = False
        if p <= seed:
            shootSucc = True

        return  shootSucc
    """
    step 4.7 判定Atk1Player、Atk2Player、Atk3Player的进攻位置；根据进攻队员位置判定Def1Player1、Def1Player2、Def2Player1、Def2Player2、Def3Player1、Def3Player2的防守位置
	4.71 根据【射门位置及系数sheet】中逻辑，将4.1~4.6所获得的球员随机到相应进攻/防守位置上
    """
    def __getAtkCoordinate(self,part):

        controller = KBEngine.entities.get(self.controllerID)
        attackObj = KBEngine.entities.get(controller.atkList[part - 1])

        pos = attackObj.pos
        curRound = "round" + str(part)
        # 候选的攻击点
        candidateList = playerAtkPosition.PlayerAtkPosition[pos][curRound]



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
        avatar = KBEngine.entities.get(self.avatarID)
        avatar.client.onTotalAttackTimes(self.totalAttackTimes)

        self.onCmdNextRound()

    # 客户端动画播放完毕
    def onCmdPlayAnimFinish(self):
        avatar = KBEngine.entities.get(self.avatarID)
        if self.endRound is True:
            ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  end round-------------------------------------------------------")
            avatar.client.onRoundEnd()
            # 进入下一轮
            self.onCmdNextRound()
            return

        if  self.curPart == 2:
            ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  2 part-------------------------------------------------------")
            self.__onSecondPart()
        if self.curPart == 3:
            ERROR_MSG("--------------------------------onCmdPlayAnimFinish---  3 part-------------------------------------------------------")
            self.__onThirdPart()

    # 客户端选择技能
    def onCmdSelectSkill(self, leftSkillIdList, rightSkillIdList):
        #
        skillId = leftSkillIdList[0]
        # ERROR_MSG( "--------------------------------onCmdSelectSkill--- part ---------" + str(self.curPart) +"       skillId   "+ str(skillId))
        if self.curPart == 1:
            if skillId == PlayerOp.passball:
                self.onCmdPass()
        elif self.curPart == 2:
            if skillId == PlayerOp.passball:
                self.onCmdPass()
            elif skillId == PlayerOp.shoot:
                self.onCmdShoot()
        elif self.curPart == 3:
            if skillId == PlayerOp.shoot:
                self.onCmdShoot()

    # 下一轮
    def onCmdNextRound(self):
        # 当前进攻序列
        self.curAttackIndex = self.curAttackIndex + 1
        avatar = KBEngine.entities.get(self.avatarID)

        # 本局结束
        if self.curAttackIndex >= self.totalAttackTimes:
            # 通知客户端统计结果 TODO：
            # self.addTimer(0, 10, TimerDefine.Timer_leave_clone)
            # ERROR_MSG("---------------------- onGameOver  --------------------------------------------------------------")
            # game over
            avatar.client.onGameOver()
            return

        avatar.client.onCurAttackIndex(self.curAttackIndex)

        # 当前攻击的是玩家还是副本
        self.__calAtkController()

        # 当前序列的第几轮
        self.curPart = 1
        #
        self.endRound = False

        controllerObj = KBEngine.entities.get(self.controllerID)
        defObj = KBEngine.entities.get(self.defenderID)

        controllerObj.atkList = []
        controllerObj.atkPosList = []
        defObj.defList = []
        defObj.preDefIds = []
        for part in range(3):
            self.__GetAttackerID(part + 1)
            self.__getDefPlayerID(part + 1)

            controllerObj = KBEngine.entities.get(self.controllerID)
            defObj = KBEngine.entities.get(self.defenderID)

            ERROR_MSG( str(part) +" - round  atk    " + str(controllerObj.atkList[part]) )
            ERROR_MSG( str(part) + " - round  defend   " + str(defObj.defList[part]))

            self.__getAtkCoordinate(part + 1)

        atkList = controllerObj.atkList
        atkPosList = controllerObj.atkPosList
        firstDefList = defObj.defList[0]
        secondDefList = defObj.defList[1]
        thirdDefList = defObj.defList[2]

        atkIDStr = "atkID      "
        for id in controllerObj.atkList:
            atkIDStr = atkIDStr + "  id  " + str(id) +" pos " +str(KBEngine.entities[id].pos)

        ERROR_MSG(atkIDStr)

        firstDefListStr = "firstDefList      "
        for id in firstDefList:
            firstDefListStr = firstDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)

        ERROR_MSG(firstDefListStr)

        secondDefListStr = "secondDefList      "
        for id in secondDefList:
            secondDefListStr = secondDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)

        ERROR_MSG(secondDefListStr)

        thirdDefListStr = "thirdDefList      "
        for id in thirdDefList:
            thirdDefListStr = thirdDefListStr + "  id  " + str(id) + " pos " + str(KBEngine.entities[id].pos)

        ERROR_MSG(thirdDefListStr)

        # ERROR_MSG("-----------------------------defObj.keeperID -------------------  " + str(defObj.keeperID) + "   objID   "+ str(defObj.id))
        avatar.client.onAtkAndDefID(atkList,atkPosList, firstDefList,secondDefList,thirdDefList,defObj.keeperID)
        # 第一步
        self.__onFirstPart()



    # 第一步
    def __onFirstPart(self,skillId = -1):
        # 副本直接选择传球
        if self.id == self.controllerID:
            self.onCmdPass()
        else:
            avatar = KBEngine.entities.get(self.avatarID)
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.select)
            pass


    # def __onFirstPartPass(self):
    #     result = self.__canSteal()
    #     avatar = KBEngine.entities.get(self.avatarID)
    #     if result is True:
    #         # 抢断成功 通知客户端播放动画
    #         self.endRound = True
    #         avatar.client.onOprateResult(self.curPart, ClientResult.trickSucc)
    #
    #         ERROR_MSG("---------onOprateResult------------trickSucc-------------------------------------------self.curPart    " + str(self.curPart))
    #     else:
    #         #  通知客户端播放完美传球动画
    #         if self.__isPerfectPassBall() is True:
    #
    #             avatar.client.onOprateResult(self.curPart, ClientResult.perfectPassBall)
    #             ERROR_MSG("---------onOprateResult------------perfectPassBall---------------------------------self.curPart    " + str(self.curPart))
    #         else:
    #             #  通知客户端播放传球动画
    #             avatar.client.onOprateResult(self.curPart, ClientResult.passBall)
    #
    #             ERROR_MSG("---------onOprateResult------------passBall-------------------------- self.curPart" + str(self.curPart))
    #
    #         self.curPart = 2
    # 第二步
    def __onSecondPart(self):

        # 如果是Npc操作（自动选择）
        if self.id == self.controllerID:

            # ERROR_MSG("------------   npc  select   -----------------------")
            self.onCloneSelectOp()
        else:
            avatar = KBEngine.entities.get(self.avatarID)
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.select)

    # 第三步
    def __onThirdPart(self):

        # 副本直接选择传球
        if self.id == self.controllerID:
            self.onCmdShoot()
        else:
            avatar = KBEngine.entities.get(self.avatarID)
            # ERROR_MSG("-------onOprateResult------player select----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.select)
            pass


    def onCmdShoot(self):
        avatar = KBEngine.entities.get(self.avatarID)
        result = self.__canSteal()
        self.endRound = True
        if result is True:
            # 抢断成功 通知客户端播放动画
            ERROR_MSG("-------onOprateResult------trickSucc----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.trickSucc)
            return True

        result = self.__isShootSucc()
        if result is True:
            # 通知客户端射门成功
            ERROR_MSG("-------onOprateResult------shootSucc 1 ----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.shootSucc)
        else:
            # 通知客户端射门失败
            ERROR_MSG("-------onOprateResult------shootFail----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.shootFail)

    # 传球
    def onCmdPass(self):

        avatar = KBEngine.entities.get(self.avatarID)
        result = self.__canSteal()
        if result is True:
            # 抢断成功 通知客户端播放动画
            ERROR_MSG("-------onOprateResult------trickSucc----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.trickSucc)
            self.endRound = True
            return True

        result = self.__isPerfectPassBall()
        if result is True:
            # 通知客户端完美传球
            ERROR_MSG("-------onOprateResult------perfectPassBall----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.perfectPassBall)
        else:
            # 通知客户端普通传球
            ERROR_MSG("-------onOprateResult------passBall----------------self.curPart  " + str(self.curPart))
            avatar.client.onOprateResult(self.curPart, ClientResult.passBall)
            # self.__onThirdPart()
        self.curPart = self.curPart + 1



    # 获得当前轮的攻击者ID
    def __getCurRoundAtkId(self,part):

        controllerObj = KBEngine.entities.get(self.controllerID)


        attackId = -1
        try:
            attackId = controllerObj.atkList[part -1]

            ERROR_MSG("------------------------self.curPart - 1    "+str(part-1 )+"   attackID-------------" +str(attackId))
        except:
            ERROR_MSG("========= list index out of range  self.curPart  =========  " + str(part-1) +"   atklist len   " + str(len(controllerObj.atkList)))

        return attackId
    # 获得当前轮的攻击者ID
    def __getCurRoundAtkCoordinate(self,part):

        controllerObj = KBEngine.entities.get(self.controllerID)


        attackCoordinate = -1
        try:
            attackCoordinate = controllerObj.atkPosList[part -1]

            ERROR_MSG("------------------------self.curPart - 1    "+str(part-1 )+"   attackCoordinate-------------" +str(attackCoordinate))
        except:
            ERROR_MSG("========= list index out of range  self.curPart  =========  " + str(part-1) +"   atklist len   " + str(len(controllerObj.atkList)))

        return attackCoordinate

    # 获得当前轮的防守者ID List
    def __getCurRoundDefList(self,part):

        defObj  = KBEngine.entities.get(self.defenderID)

        defList = defObj.defList[part - 1]

        return defList

    # 副本AI(副本选择射门还是传球)
    def onCloneSelectOp(self):
        # 计算射门值
        p = self.__getShootValue()

        # ERROR_MSG("              =========  onCloneSelectOp         ====================  p     "  + str(p))
        if p >= 0.4:
            # 射门
            self.onCmdShoot()
        else:
            # 传球
            self.onCmdPass()





    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        DEBUG_MSG(tid, userArg)
        if userArg == TimerDefine.Timer_leave_clone:
            avatar = KBEngine.entities.get(self.avatarID)
            avatar.base.onClientLeaveClone()




    def onDestroy(self):
        """
        KBEngine method.
        """
        del KBEngine.globalData["room_%i" % self.spaceID]
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


#=========================================================================
    def setAvatarID(self,avatarID):

        self.avatarID = avatarID

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
class PlayerOp:
    passball = 1
    shoot = 2